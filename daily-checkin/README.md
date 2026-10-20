# Daily Check-in

A phone app where an older adult does a 2-minute spoken check-in each day, based on the 4AT delirium screen. Their family sees a plain result ("Looks like their usual self", "Keep an eye on it", "Call their doctor today") with the reasons. If the check-in is skipped, the family gets a text.

**Screening only, not a diagnosis.**

## What's here

| Folder | What it is |
| --- | --- |
| `server/` | Python API: the daily questions, answer scoring, voice features, each person's baseline, the change model, missed check-in alerts |
| `app/` | Expo (React Native) app for iPhone, Android and web. Senior mode and family mode in one app |
| `supabase/schema.sql` | The same tables for Supabase (Postgres), with row-level security |

## How a check-in is scored

1. **Alertness:** no reply to most questions, or much slower and briefer than their usual, scores 4.
2. **Orientation (AMT4):** age, date of birth, where they are, and the year. Asked every day in a different order and wording. 0 mistakes = 0, 1 = 1, 2+ = 2. Answers the rules can't settle (e.g. "in the kitchen") can go to Claude for a second opinion, or are flagged for a person to check. They are never counted as a mistake.
3. **Attention:** months backwards (the 4AT's own task) every other day. On the other days it's days of the week backwards or counting down from 20, which are adaptations. Scored on the same 7-of-12 share.
4. **Acute change:** scores 4 if the family says "they seem different today", or if the voice model says today is far from their own normal.

The total uses the 4AT bands: 4+ is "Call their doctor today", 1 to 3 is "Keep an eye on it", and 0 is "Looks like their usual self".

**Voice model.** It measures response delay, speaking rate, pauses, "um/uh" rate, repeated words and how much they say. Each measure is compared to that person's own last 2 to 14 usual days, and a logistic model turns the differences into a probability. A single "um" or repeated word can't push it far on its own: those two measures count at most 1.5 times their usual spread. **The shipped model (`server/checkin/model.json`) is trained on simulated people**, so its 0.99 score on held-out people means nothing about real accuracy. Retrain it on real recordings (see below).

**Missed check-ins.** The senior gets a reminder at their check-in time and again an hour later. After 3 hours the family gets "Mom hasn't done today's check-in. Give her a call." Two missed days in a row sends a stronger message. Families can mark days off. A check-in 3+ hours later than usual is also noted.

## Run it

```bash
# Server
cd server
python3 -m pip install -r requirements.txt
python3 -m pytest
python3 -m checkin.demo                # optional: a demo senior with a week of history
DEMO_MODE=1 uvicorn checkin.api:app --host 0.0.0.0 --port 8000

# App (another terminal)
cd app
npm install
EXPO_PUBLIC_API_URL=http://<your computer's LAN IP>:8000 npx expo start
```

Scan the QR code with Expo Go on a phone that's on the same Wi-Fi. Press `w` for the web version, which types answers instead of using the microphone unless you set `EXPO_PUBLIC_WEB_MIC=1`.

## Keys and settings (all optional; nothing is sent anywhere without them)

| Setting | What it turns on |
| --- | --- |
| `STT_PROVIDER=local` | Free speech-to-text for recorded answers: Whisper runs on the server (`pip install -r requirements-local.txt`, plus ffmpeg). `LOCAL_WHISPER_MODEL` picks the weights, either a Hugging Face id (default `openai/whisper-small`; `small.en` is more accurate in a quiet room but far worse with a TV in the background) or the folder of the model fine-tuned on older voices. Whisper tends to drop "um" and "uh", so the filler measure is weaker with it. |
| `STT_PROVIDER=parakeet` | Another free option: NVIDIA Parakeet TDT 0.6B v2 on the CPU. `pip install sherpa-onnx`, unpack `sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8` from the sherpa-onnx releases, and set `PARAKEET_DIR` to it. |
| `STT_PROVIDER=deepgram` + `DEEPGRAM_API_KEY` | Paid alternative that keeps fillers (or `STT_PROVIDER=openai` + `OPENAI_API_KEY`). Without any provider, only typed answers work. |
| `JUDGE_ENABLED=1` + `ANTHROPIC_API_KEY` | Claude double-checks answers the rules can't settle |
| `NOTIFY_LIVE=1` + `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM` | Real texts to the family. Without it, alerts are only recorded and shown in the family view. |
| `API_TOKEN` (server) + `EXPO_PUBLIC_API_TOKEN` (app) | Requires a shared token on every request |
| `DEMO_MODE=1` | Lets you set the date or time on requests, for demos and tests. Turn it off for real users. |

Run the missed check-in job every 10 minutes: `curl -X POST http://<server>/jobs/missed-checkins` (from cron, Supabase `pg_cron`, or any scheduler).

## Testing with families (plan days 6 to 9)

Start with [HOME-TESTING.md](HOME-TESTING.md). It covers getting the app onto testers' phones with Expo Go, what to do each day (quiet days first, then TV and other noise), and getting the results back.

- **Hand scoring:** download `GET /export/hand-scoring.csv`, which has one row per answer with a link to its recording. Listen, and fill `hand_score` with `right` or `wrong`, or for the backwards task the number of items said in order. Send the file back with `curl -X POST --data-binary @sheet.csv http://<server>/import/hand-scoring`.
- **The numbers:** `python3 -m checkin.report` (or `GET /reports/testing?format=md`) prints the evidence-slide table. It covers days checked in, agreement with hand scoring, check-in length, the senior's 1 to 5 ease rating (asked at the end of each check-in), and how many missed check-in alerts families said were real (they answer in the family view).

## Retraining the model on real check-ins (plan day 5)

1. Record check-ins from yourself and volunteers. Do some normally and some while tired or distracted.
2. `curl http://<server>/export/features.csv > rows.csv`, then fill the `label` column with `normal` or `off`.
3. `python3 -m checkin.train --csv rows.csv`. It reports accuracy on held-out people and overwrites `model.json`.

## Known gaps

- Recorded answers get common speech-to-text slips fixed before scoring ("eighty too", "20/26", a countdown heard as "1918"). When a clip has speech but the transcript can't be an answer, the app asks the question once more (the server's `POST /people/{id}/answers/check` says when); if it still can't be made out, it's left for a person to check rather than counted wrong. On the months-backwards question, speech-to-text is primed with the month list, and an answer that would pass with exactly one month missing is asked again (dropped months were the main false alarm in the project's tests). With loud background TV, every model tested still makes healthy people look impaired too often, so the app listens to the room before the first question and asks them to turn the TV down if it's loud (the threshold, `NOISY_ROOM_DB` in `CheckIn.tsx`, is a guess that needs tuning on real phones). If two answers in a row have another voice in the background (the gaps between words flicker like speech and aren't much quieter than the person's voice), the app asks once per check-in whether a TV or radio is on, and asks the question again once it's off. Noisy check-ins are kept out of the voice baseline, and a flagged noisy day tells the family some answers may have been misheard.

- Not tested on a real phone yet. The microphone, the quiet-detection threshold (`SPEAKING_DB` in `CheckIn.tsx`) and spoken prompts need a check on iPhone and Android.
- Server push notifications need a development build (`eas build --profile development`), because Expo Go no longer supports remote push on Android. The daily reminder is scheduled on the phone itself and works in Expo Go.
- Data is stored in SQLite. `supabase/schema.sql` is ready for the move, but the server doesn't talk to Supabase yet.
- Login is a shared code plus an optional API token. Give families real accounts (Supabase Auth) before anyone outside your test group uses it.
- Recordings are kept in `server/data/audio/` until `DELETE /people/{id}/recordings` is called. Delete them after testing, as the consent form says.
