# From prototype to an installable app

The steps to get Daily Check-in onto people's phones as a real app, in order. Each step says who does it. "Claude" steps need nothing from you; "You" steps need your decision, an account in your name, or money.

## 1. Show it works on real people (before any launch)

No other tool screens for delirium at home by voice (see the competitor notes), so "better than the others" really means "accurate enough on real people". The model hasn't shown that yet: the voice model is trained on simulated people and nothing has been tested on real delirium recordings.

| Step | Who |
| --- | --- |
| Run the home phone test (HOME-TESTING.md): 5+ days per tester, quiet days then TV days | You and testers |
| Hand-score the answers and print the results table (`checkin.report`) | Claude, once results come in |
| Retrain the voice model on real check-ins (`checkin.train`) and recheck the change-score weights | Claude, once results come in |
| Test on real delirium speech. That needs data from a hospital or research group, which means contacting them; that's on hold until you say otherwise | You decide |

## 2. Installable test builds (free)

Done in this PR: app IDs (`com.north2.dailycheckin`), build profiles in `app/eas.json`, a development build client, a server address you can change from the setup screen (so one build works with any server), and a `server/Dockerfile`.

| Step | Who |
| --- | --- |
| Make a free Expo account at expo.dev; Claude can't sign up for you | You |
| `cd app && npx eas-cli login && npx eas-cli init` (links the project to your account, adds a project id to `app.json`) | You, or Claude on your PC once you're logged in |
| Put the server somewhere phones can reach over HTTPS. Free for testing: run it on your PC and expose it with `cloudflared tunnel --url http://localhost:8000` (no account; the address changes each run, so type it into the app's "Server: … (change)" link) | You pick where |
| Android test build: `npx eas-cli build --profile preview --platform android`. Gives an APK link testers install directly. Free tier, waits in a queue | Claude, after you log in |
| iPhone test build: needs an Apple Developer account ($99/year). Until then iPhone testers keep using Expo Go | You decide (money) |

Android release builds refuse plain `http://` addresses, so the test build needs the HTTPS tunnel or a hosted server, not a LAN address.

## 3. Before real users (not just testers)

| Step | Who |
| --- | --- |
| Real family accounts (Supabase Auth) instead of the shared code; move data from SQLite to Supabase | Claude |
| Server push notifications through the development/production build | Claude |
| Turn off `DEMO_MODE`, set `API_TOKEN`, and delete test recordings | Claude |
| Privacy policy and in-app consent text (store listings require a privacy policy URL) | Claude drafts, you approve |
| Paid hosting for the server, or keep it on your PC | You decide (money) |

## 4. Medical-device rules (your call, before any store)

A tool that tells families to "call their doctor today" about possible delirium is likely to count as software as a medical device: in the US the FDA regulates software that screens for or helps diagnose a condition, and the UK (MHRA) and EU (MDR) have similar rules. In practice:

- Launching as a medical screener means clearance (for example FDA 510(k) or De Novo), a quality system and clinical evidence. That's months and real money.
- The alternative is a narrower "general wellness / family check-in" product that doesn't claim to detect delirium, which changes the wording across the app.
- Apple and Google both review health apps and can reject ones that make medical claims without clearance.

This needs a person to decide, ideally with advice from a regulatory specialist. Claude hasn't changed any wording for it.

## 5. Store release

| Step | Who |
| --- | --- |
| Google Play developer account ($25 once) and Apple developer account ($99/year) | You (money) |
| Store screenshots, description and listing text | Claude drafts, you approve |
| `npx eas-cli build --profile production` then `npx eas-cli submit` | Claude, only after you say to submit |
| Making the code public, if you ever want to | You decide |
