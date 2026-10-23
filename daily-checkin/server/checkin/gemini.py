"""Google Gemini, for listening to recorded answers. Everything here is off
unless a flag turns it on, and every caller falls back to what the app does
without Gemini when a call fails or times out.

  GEMINI_TRANSCRIBE=1    Gemini writes the transcript; Whisper (or whichever
                         STT_PROVIDER) still gives the word timings that the
                         voice measures use. See transcribe.transcribe_detail.
  GEMINI_SPEECH_NOTE=1   Gemini also rates how unusual the speech sounds
                         (0 to 3), a small capped extra in change.py.
  JUDGE_ENGINE=gemini    with JUDGE_ENABLED=1, Gemini listens to answers the
                         rules can't settle (judge.py) instead of Claude
                         reading their transcript.

Backends:
  Vertex AI (production): GOOGLE_CLOUD_PROJECT, optional GOOGLE_CLOUD_LOCATION
    (default us-central1), application default credentials (google-auth if
    installed, otherwise the metadata server on Google Cloud). Use a project
    with zero data retention and a BAA before real people's voices go there.
  Developer API (testing): GEMINI_API_KEY. The free tier may use what it is
    sent, so only send synthetic or public audio with a free key.
Vertex wins when both are set; GEMINI_BACKEND=vertex|developer overrides.

GEMINI_MODEL pins the model (default gemini-3.6-flash). "-latest" aliases are
refused: when the model behind a name changes, transcripts and ratings shift
and people's comparisons with their own normal days break.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import os
import time
import wave

import httpx

log = logging.getLogger(__name__)

# gemini-2.5-flash, the first choice, is closed to new Developer API keys
# (404 "no longer available to new users", checked 2026-10-22).
DEFAULT_MODEL = "gemini-3.6-flash"
DEFAULT_LOCATION = "us-central1"
DEFAULT_TIMEOUT_S = 8.0


class GeminiUnavailable(RuntimeError):
    pass


def _flag(name: str) -> bool:
    return os.environ.get(name) == "1"


def model() -> str:
    return os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL


def backend() -> str | None:
    forced = os.environ.get("GEMINI_BACKEND")
    vertex, developer = bool(os.environ.get("GOOGLE_CLOUD_PROJECT")), bool(os.environ.get("GEMINI_API_KEY"))
    if forced == "vertex" or (forced is None and vertex):
        return "vertex" if vertex else None
    if forced in (None, "developer") and developer:
        return "developer"
    return None


def configured() -> bool:
    return backend() is not None and "latest" not in model()


def transcribe_enabled() -> bool:
    return _flag("GEMINI_TRANSCRIBE") and configured()


def speech_note_enabled() -> bool:
    return _flag("GEMINI_SPEECH_NOTE") and configured()


def status() -> dict:
    """What /health shows: which Gemini features are on, never the key."""
    return {
        "backend": backend(),
        "model": model() if backend() else None,
        "transcribe": transcribe_enabled(),
        "speech_note": speech_note_enabled(),
        "judge": os.environ.get("JUDGE_ENABLED") == "1" and os.environ.get("JUDGE_ENGINE") == "gemini"
        and configured(),
        "refused_model": "latest" in model(),
    }


def timeout_s() -> float:
    try:
        return float(os.environ.get("GEMINI_TIMEOUT_S") or DEFAULT_TIMEOUT_S)
    except ValueError:
        return DEFAULT_TIMEOUT_S


def _url() -> str:
    m = model()
    if backend() == "vertex":
        project = os.environ["GOOGLE_CLOUD_PROJECT"]
        loc = os.environ.get("GOOGLE_CLOUD_LOCATION") or DEFAULT_LOCATION
        host = "aiplatform.googleapis.com" if loc == "global" else f"{loc}-aiplatform.googleapis.com"
        return f"https://{host}/v1/projects/{project}/locations/{loc}/publishers/google/models/{m}:generateContent"
    return f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"


_token: dict = {}


def _access_token() -> str:
    """An OAuth token from application default credentials, kept until a
    minute before it expires."""
    if _token.get("value") and _token.get("expires", 0) > time.time() + 60:
        return _token["value"]
    try:
        import google.auth
        import google.auth.transport.requests

        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        creds.refresh(google.auth.transport.requests.Request())
        value, expires = creds.token, (creds.expiry.timestamp() if creds.expiry else time.time() + 300)
    except ImportError:
        # On Google Cloud (Cloud Run, GKE, Compute Engine) without google-auth.
        r = httpx.get("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
                      headers={"Metadata-Flavor": "Google"}, timeout=5)
        r.raise_for_status()
        body = r.json()
        value, expires = body["access_token"], time.time() + float(body.get("expires_in", 300))
    _token.update(value=value, expires=expires)
    return value


def _headers() -> dict:
    if backend() == "vertex":
        return {"Authorization": f"Bearer {_access_token()}"}
    return {"x-goog-api-key": os.environ["GEMINI_API_KEY"]}


def _thinking() -> dict | None:
    """As little thinking as the model allows: listening doesn't need it, and
    it slows the answer down (gemini-3.6-flash: about 4.5 s with its default
    thinking, 2.8 s with "low", on a short synthetic answer).
    GEMINI_THINKING_LEVEL overrides it for Gemini 3 models."""
    m = model()
    if m.startswith("gemini-2.5-flash"):
        return {"thinkingBudget": 0}
    if m.startswith("gemini-3"):
        return {"thinkingLevel": os.environ.get("GEMINI_THINKING_LEVEL") or "low"}
    return None


def generate(parts: list[dict], schema: dict, timeout: float | None = None) -> dict:
    """One generateContent call that must answer with JSON matching schema.
    Raises GeminiUnavailable on any failure; callers fall back."""
    if not configured():
        raise GeminiUnavailable("Gemini isn't configured (or GEMINI_MODEL is a -latest alias)")
    config: dict = {"temperature": 0, "responseMimeType": "application/json", "responseSchema": schema}
    thinking = _thinking()
    if thinking:
        config["thinkingConfig"] = thinking
    body = {"contents": [{"role": "user", "parts": parts}], "generationConfig": config}
    try:
        r = httpx.post(_url(), headers=_headers(), json=body, timeout=timeout or timeout_s())
        r.raise_for_status()
        cand = r.json()["candidates"][0]
        text = "".join(p.get("text", "") for p in cand["content"]["parts"])
        return json.loads(text)
    except Exception as e:  # network, HTTP, auth, blocked or malformed output: all mean "no answer"
        # Never log the body: it can hold what the person said.
        log.warning("Gemini call failed: %s", type(e).__name__)
        raise GeminiUnavailable(type(e).__name__) from e


def wav_16k(samples) -> bytes:
    """16 kHz mono 16-bit WAV, a format every Gemini backend accepts (phone
    m4a and browser webm aren't on the list)."""
    import numpy as np

    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2").tobytes()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(pcm)
    return buf.getvalue()


def audio_part(wav: bytes) -> dict:
    return {"inlineData": {"mimeType": "audio/wav", "data": base64.b64encode(wav).decode()}}


# The transcription instruction says nothing about the question, the right
# answer or the person, so Gemini can't hear what it expects to hear.
TRANSCRIBE_PROMPT = (
    "Transcribe the main speaker in this recording verbatim, exactly as spoken, "
    "including filler words (um, uh), repetitions, false starts and mistakes. "
    "Do not correct or complete anything. Leave out background voices, TV, radio "
    "and other people. Write numbers as digits. If the main speaker says nothing, "
    "return an empty transcript."
)
NOTE_SCALE = (
    "from 0 to 3: 0 clear and ordinary for an older adult; 1 slightly hesitant or "
    "effortful; 2 clearly unusual (marked confusion, slurring, long hesitations, "
    "trailing off); 3 very unusual. Judge only how the speech sounds and flows, not "
    "whether anything said is right. Give a short reason of at most 12 words."
)
NOTE_PROMPT = "Also rate how unusual the main speaker's speech sounds, " + NOTE_SCALE
NOTE_ONLY_PROMPT = ("Rate how unusual the main speaker's speech in this recording sounds, ignoring "
                    "background voices, TV and other people, " + NOTE_SCALE)


def listen(wav: bytes, transcript: bool, note: bool, timeout: float | None = None) -> dict:
    """{"transcript"?: str, "unusual"?: {"rating": 0-3, "reason": str}} for
    one clip, in one call."""
    props: dict = {}
    if transcript:
        props["transcript"] = {"type": "STRING"}
    if note:
        props["unusual_rating"] = {"type": "INTEGER"}
        props["unusual_reason"] = {"type": "STRING"}
    if not props:
        return {}
    prompt = (TRANSCRIBE_PROMPT + (" " + NOTE_PROMPT if note else "")) if transcript else NOTE_ONLY_PROMPT
    schema = {"type": "OBJECT", "properties": props, "required": list(props)}
    out = generate([audio_part(wav), {"text": prompt}], schema, timeout)
    heard: dict = {}
    if transcript:
        if not isinstance(out.get("transcript"), str):
            raise GeminiUnavailable("no transcript in the reply")
        heard["transcript"] = out["transcript"].strip()
    if note:
        try:
            rating = max(0, min(3, int(out["unusual_rating"])))
            heard["unusual"] = {"rating": rating, "reason": str(out.get("unusual_reason", ""))[:200]}
        except (KeyError, TypeError, ValueError):
            pass  # a transcript without a rating is still a transcript
    return heard
