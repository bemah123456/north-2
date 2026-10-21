# Testing on real phones at home

The goal is to find out how the app does on real phones, in real rooms, before the Oct 26 deadline. We want answers to three questions. How often does it mark a right answer wrong? How much worse is it with a TV on? Do people finish the check-in in under 3 minutes and find it easy? The results go on the evidence slide.

Plan for Oct 21 to 25: each tester does one check-in a day for at least 5 days.

## 1. Set up the server (one laptop, once)

The laptop stays on and awake for the whole test. Every phone talks to it.

```bash
cd daily-checkin/server
python3 -m pip install -r requirements.txt -r requirements-local.txt   # plus ffmpeg
export STT_PROVIDER=local                  # Whisper small, free, runs on the laptop
export API_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
echo $API_TOKEN                            # the app needs this too
uvicorn checkin.api:app --host 0.0.0.0 --port 8000
```

Leave `DEMO_MODE` off for real testing.

Phones at home aren't on the laptop's Wi-Fi, so give the server a public https address. The free way is Cloudflare's quick tunnel, which needs no account:

```bash
cloudflared tunnel --url http://localhost:8000   # prints https://<random>.trycloudflare.com
```

Open `https://<random>.trycloudflare.com/health` on your phone to check it works. The address changes every time cloudflared restarts. If it does, each tester taps "Server settings" on the app's first screen and types in the new address. Phones that are already set up need "Change setup" first.

## 2. Put the app on the phones

Each tester installs **Expo Go** from the App Store or Google Play. The app uses Expo SDK 58, which the current Expo Go supports. Then, on the laptop:

```bash
cd daily-checkin/app
npm install
EXPO_PUBLIC_API_URL=https://<random>.trycloudflare.com EXPO_PUBLIC_API_TOKEN=<API_TOKEN> npx expo start --tunnel
```

`--tunnel` gives a QR code that works from any network. Testers scan it with the camera (iPhone) or with Expo Go (Android). Expo Go remembers the project under "Recently opened".

This only works while `expo start` is running on the laptop. If that's a problem for a tester, an Android tester can install a test build instead. [LAUNCH.md](LAUNCH.md) has the steps. It needs a free Expo account in a team member's name.

In the app:
- **Testing on yourself:** pick "I'm setting this up for a family member", fill in your own details, then "This is their phone: start check-ins".
- **A volunteer with a helper:** the helper creates the profile on their own phone and gives the code to the volunteer's phone ("My family gave me a code").

## 3. What to do each day

Do one check-in a day at about the same time. Hold the phone the way you normally would.

| Days | Room | Why |
| --- | --- | --- |
| 1 to 5 | Quiet: TV and radio off, door closed | Builds the person's own normal, which needs 5 quiet days |
| 6 | TV on at normal volume, across the room | The main false-alarm risk in our tests |
| 7 | One of: a fan or AC on, the kitchen with a tap running, or another person talking nearby | Other everyday noise |
| Optional extra | Phone on a table instead of in hand; speakerphone volume low | Microphone distance |

**Evening check-in:** for one tester, turn on the evening check-in in the family view ("Evening check-in: off", then "Turn it on") from day 3. It's about a minute, an hour before the time set (7 pm by default). That tests whether a normal evening is wrongly flagged as worse than the morning.

**Team members only:** on one extra check-in, give some wrong answers on purpose, such as the wrong year, skipping months, or getting the numbers in the digit task wrong. If you're testing the evening check-in, do one scripted evening that's worse than that morning. This checks that the app catches them. Write "scripted" in the log, so these check-ins are kept apart from the real false-alarm numbers. Never ask an older volunteer to do this.

After each check-in, add a row to [test-log.csv](test-log.csv): the date, who it was, the phone model, morning or evening, the room, and anything odd. For example, "it asked me to turn the TV down", "it re-asked the year", or "it crashed".

## 4. Volunteers and recordings

- Only test healthy volunteers who agreed to it. This is not for anyone who is unwell or in hospital.
- Tell them each answer is recorded and kept on the team laptop. It's used only to check the app and is deleted after the hackathon.
- To delete one person's recordings: `curl -X DELETE -H "Authorization: Bearer $API_TOKEN" http://localhost:8000/people/<id>/recordings`.

## 5. Getting the results back

At the end, on the laptop:

```bash
H="Authorization: Bearer $API_TOKEN"
curl -H "$H" http://localhost:8000/export/hand-scoring.csv > hand-scoring.csv
```

1. Open `hand-scoring.csv`. For each row, play the recording. The `file` column is its path on the laptop, which opens without the token. Then fill in `hand_score`. Use `right` or `wrong`. For the backwards tasks and the four-number digit task, write the number of items said in the right order. The `noisy_room` column shows when the app thought the room was noisy.
2. Send it back: `curl -H "$H" -X POST --data-binary @hand-scoring.csv http://localhost:8000/import/hand-scoring`.
3. Run `python3 -m checkin.report` in `daily-checkin/server` for the evidence-slide table. It splits agreement with hand scoring by quiet room and noisy room.
4. Upload `hand-scoring.csv`, `test-log.csv` and the report to the project. Claude can then work out the false-alarm rate for each room type and add the numbers to the deck.
5. Optional: `curl -H "$H" http://localhost:8000/export/features.csv > rows.csv`, then label each row `normal` or `off` (scripted) to retrain the voice model. See the README.
