"""Speech-to-text with word timestamps.

Set STT_PROVIDER to one of:
  "local"     free: Whisper running on this server (pip install -r
              requirements-local.txt). LOCAL_WHISPER_MODEL picks the
              weights: a Hugging Face id (default openai/whisper-small;
              small.en is more accurate in a quiet room but much worse with
              a TV on) or a folder, such as the model fine-tuned on older
              voices.
  "parakeet"  free: NVIDIA Parakeet TDT 0.6B v2 on the CPU (pip install
              sherpa-onnx; unpack sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8
              from the sherpa-onnx releases and set PARAKEET_DIR to it)
  "deepgram"  paid: DEEPGRAM_API_KEY
  "openai"    paid: OPENAI_API_KEY (Whisper API)
Without any of them, the API still accepts answers that arrive already
transcribed (the typed demo mode).
"""

from __future__ import annotations

import os
import subprocess
import tempfile

import httpx

from .features import Word


class TranscriptionUnavailable(RuntimeError):
    pass


def provider() -> str | None:
    p = os.environ.get("STT_PROVIDER")
    if p in ("local", "parakeet"):
        return p
    if p == "deepgram" and os.environ.get("DEEPGRAM_API_KEY"):
        return p
    if p == "openai" and os.environ.get("OPENAI_API_KEY"):
        return p
    return None


# Whisper often drops one month from a spoken list, which makes a healthy
# person fail months backwards. Priming it with the list fixed that in the
# project's tests (Whisper small: 0% false alarms on clean audio, 2% with
# noise) without making it invent months for wrong answers.
MONTHS_BACKWARDS = ("December, November, October, September, August, July, June, May, "
                    "April, March, February, January.")


def transcribe(audio: bytes, content_type: str, expect: str | None = None) -> tuple[str, list[Word]]:
    """expect: words the answer is likely to contain, such as
    MONTHS_BACKWARDS for the months question. Providers that can be primed
    with it are; the others ignore it."""
    p = provider()
    if p == "local":
        return _local_whisper(audio, expect)
    if p == "parakeet":
        return _parakeet(audio)
    if p == "deepgram":
        return _deepgram(audio, content_type, expect)
    if p == "openai":
        return _whisper(audio, content_type, expect)
    raise TranscriptionUnavailable("No speech-to-text provider configured")


SR = 16000


def _decode_16k(audio: bytes):
    """Any format ffmpeg reads (phone m4a, browser webm, wav) to 16 kHz mono.
    Goes through a temporary file: Android, and often iOS, write the m4a
    index after the audio, which ffmpeg can't read from a pipe."""
    import numpy as np

    with tempfile.NamedTemporaryFile(suffix=".audio") as f:
        f.write(audio)
        f.flush()
        p = subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-i", f.name, "-f", "f32le", "-ac", "1", "-ar", str(SR), "pipe:1"],
            capture_output=True,
        )
    if p.returncode != 0:
        raise TranscriptionUnavailable("Could not decode the recording: " + p.stderr.decode(errors="replace")[-200:])
    return np.frombuffer(p.stdout, dtype=np.float32)


def has_speech(audio: bytes) -> bool | None:
    """Whether a clip has speech in it. None when it can't be decoded here."""
    check = clip_check(audio)
    return check["heard_speech"] if check else None


def background_flicker(x, sr: int = SR) -> float:
    """Mean frame-to-frame loudness change (dB) across the quietest 40% of
    30 ms frames: the gaps around the person's words. A TV or radio fills
    the gaps with speech, which flickers (about 5 to 9 dB); a fan, hiss or
    a quiet room is steady (under about 4 dB). From the project's speech
    comparison (research/cloud-4at-asr), tuned on synthetic audio only."""
    import numpy as np

    frame = int(0.03 * sr)
    n = len(x) // frame
    if n < 10:
        return 0.0
    rms = np.sqrt((x[: n * frame].reshape(n, frame) ** 2).mean(axis=1))
    db = 20 * np.log10(np.maximum(rms, 1e-4))
    quiet = db[db <= np.percentile(db, 40)]
    return float(np.abs(np.diff(quiet)).mean()) if len(quiet) > 2 else 0.0


# Above this, the gaps probably hold someone else talking. It flagged 96% of
# clips with a TV 20 dB below the speaker, no steady fan noise, and about
# 5% of quiet clips.
TV_FLICKER_DB = 4.4


def clip_check(audio: bytes) -> dict | None:
    """heard_speech: some 30 ms frame stands well above the quietest ones (by
    a smaller margin when there's background sound, since the gaps aren't
    quiet).
    noisy: another voice, such as a TV, seems to be talking in the gaps;
    with one on, every speech model we tested mishears healthy answers far
    more often. None when the clip can't be decoded here."""
    import numpy as np

    try:
        x = _decode_16k(audio)
    except (TranscriptionUnavailable, FileNotFoundError):
        return None
    frame = int(0.03 * SR)
    n = len(x) // frame
    if n < 3:
        return {"heard_speech": False, "noisy": False}
    e = np.sqrt((x[: n * frame].reshape(n, frame) ** 2).mean(axis=1)) + 1e-6
    floor = np.percentile(e, 10)
    heard = bool(e.max() > 0.01 and e.max() / floor > (3 if floor > 0.003 else 10))
    noisy = background_flicker(x) > TV_FLICKER_DB
    return {"heard_speech": heard, "noisy": noisy}


def _deepgram(audio: bytes, content_type: str, expect: str | None = None) -> tuple[str, list[Word]]:
    params = [("model", "nova-3"), ("filler_words", "true"), ("smart_format", "false")]
    if expect:
        params += [("keyterm", w.strip(" ,.")) for w in expect.split()]
    r = httpx.post(
        "https://api.deepgram.com/v1/listen",
        params=params,
        headers={
            "Authorization": f"Token {os.environ['DEEPGRAM_API_KEY']}",
            "Content-Type": content_type or "audio/m4a",
        },
        content=audio,
        timeout=60,
    )
    r.raise_for_status()
    alt = r.json()["results"]["channels"][0]["alternatives"][0]
    words = [Word(w["word"], float(w["start"]), float(w["end"])) for w in alt.get("words", [])]
    return alt.get("transcript", ""), words


def _whisper(audio: bytes, content_type: str, expect: str | None = None) -> tuple[str, list[Word]]:
    ext = {"audio/webm": "webm", "audio/wav": "wav", "audio/mpeg": "mp3"}.get(content_type, "m4a")
    r = httpx.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        data={
            "model": "whisper-1",
            "response_format": "verbose_json",
            "timestamp_granularities[]": "word",
            # Whisper drops "um" and "uh" unless the prompt shows them.
            "prompt": "Umm, let me think, uh, hmm." + (" " + expect if expect else ""),
        },
        files={"file": (f"answer.{ext}", audio, content_type or "audio/m4a")},
        timeout=60,
    )
    r.raise_for_status()
    body = r.json()
    words = [Word(w["word"], float(w["start"]), float(w["end"])) for w in body.get("words", [])]
    return body.get("text", ""), words


DEFAULT_LOCAL_MODEL = "openai/whisper-small"
_local_pipeline = None


def _load_local():
    global _local_pipeline
    if _local_pipeline is None:
        try:
            from transformers import pipeline
        except ImportError as e:
            raise TranscriptionUnavailable("Install requirements-local.txt to use local Whisper") from e
        _local_pipeline = pipeline(
            "automatic-speech-recognition",
            model=os.environ.get("LOCAL_WHISPER_MODEL", DEFAULT_LOCAL_MODEL),
            device=os.environ.get("LOCAL_WHISPER_DEVICE", "cpu"),
        )
    return _local_pipeline


def _local_whisper(audio: bytes, expect: str | None = None) -> tuple[str, list[Word]]:
    model = os.environ.get("LOCAL_WHISPER_MODEL", DEFAULT_LOCAL_MODEL)
    # English-only checkpoints (".en") reject a language setting.
    gen = {} if model.endswith(".en") else {"language": "english", "task": "transcribe"}
    samples = _decode_16k(audio)
    if len(samples) < SR // 10:  # under 0.1 s: nothing to transcribe
        return "", []
    pipe = _load_local()
    clip = {"raw": samples, "sampling_rate": SR}
    out = None
    if expect:
        try:
            primed = gen | {"prompt_ids": pipe.tokenizer.get_prompt_ids(expect, return_tensors="pt")}
            out = pipe(dict(clip), return_timestamps="word", generate_kwargs=primed)
        except Exception:  # an older transformers without prompts: transcribe plainly
            out = None
    if out is None:
        out = pipe(clip, return_timestamps="word", **({"generate_kwargs": gen} if gen else {}))
    words = []
    for chunk in out.get("chunks", []):
        start, end = chunk["timestamp"]
        text = chunk["text"].strip()
        if text and start is not None:
            words.append(Word(text, float(start), float(end if end is not None else start)))
    return out.get("text", "").strip(), words


_parakeet_recognizer = None


def _parakeet(audio: bytes) -> tuple[str, list[Word]]:
    global _parakeet_recognizer
    x = _decode_16k(audio)
    if len(x) < SR // 10:
        return "", []
    if _parakeet_recognizer is None:
        try:
            import sherpa_onnx
        except ImportError as e:
            raise TranscriptionUnavailable("pip install sherpa-onnx to use Parakeet") from e
        d = os.environ.get("PARAKEET_DIR")
        if not d:
            raise TranscriptionUnavailable("Set PARAKEET_DIR to the unpacked Parakeet model")
        _parakeet_recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=os.path.join(d, "encoder.int8.onnx"),
            decoder=os.path.join(d, "decoder.int8.onnx"),
            joiner=os.path.join(d, "joiner.int8.onnx"),
            tokens=os.path.join(d, "tokens.txt"),
            model_type="nemo_transducer",
            num_threads=int(os.environ.get("PARAKEET_THREADS", "4")),
        )
    s = _parakeet_recognizer.create_stream()
    s.accept_waveform(SR, x)
    _parakeet_recognizer.decode_stream(s)
    r = s.result
    durations = list(getattr(r, "durations", []) or [0.0] * len(r.tokens))
    return r.text.strip(), _words_from_tokens(list(r.tokens), list(r.timestamps), durations)


def _words_from_tokens(tokens: list[str], starts: list[float], durations: list[float]) -> list[Word]:
    """Join sub-word tokens into words. A token starting with a space
    begins a new word; punctuation stays with the word before it."""
    words: list[Word] = []
    for tok, start, dur in zip(tokens, starts, durations):
        end = float(start) + max(float(dur), 0.0)
        if tok.startswith(" ") or not words:
            if tok.strip():
                words.append(Word(tok.strip(), float(start), end))
        else:
            last = words[-1]
            words[-1] = Word(last.text + tok, last.start, max(last.end, end))
    return words
