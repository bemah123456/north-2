from checkin.features import Word


def spoken(text: str, latency: float = 1.0, words_per_min: float = 130, pause_every: int = 0,
           pause: float = 1.0) -> list[Word]:
    """Fake word timestamps for a transcript, as speech-to-text would return."""
    step = 60.0 / words_per_min
    t = latency
    out = []
    for i, w in enumerate(text.split()):
        if pause_every and i and i % pause_every == 0:
            t += pause
        out.append(Word(w, t, t + step * 0.8))
        t += step
    return out
