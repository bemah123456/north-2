# Daily Check-in Android test app

File: `daily-checkin-test.apk` (36 MB, kept in the Claude project files under `launch/`, not in this repo). Built 2026-10-20 from the senior-friendly redesign (PR #15, now merged). Nothing was published anywhere and no Expo account was used.

SHA-256: `288af63221fe41e70c7926b0b1187257f6554fc927e150fd9026ac197ecf12b6`

## Put it on an Android phone (Android 7 or newer)

1. Get the `.apk` file onto the phone: email it to yourself, put it in Google Drive, or copy it over a USB cable into the phone's Download folder.
2. On the phone, open the file (from Files, Downloads, Drive or the email).
3. If the phone says it can't install apps from this source, tap **Settings**, turn on **Allow from this source**, then go back and tap **Install**.
4. If Google Play Protect warns that it doesn't recognise the app, tap **More details → Install anyway**. That's normal for a test app that isn't on the Play Store.
5. Open **Daily Check-in** and allow the microphone and notifications when it asks.

## Point it at the server

The app needs the check-in server running somewhere the phone can reach.

- On your PC, in `daily-checkin/server`: `DEMO_MODE=1 uvicorn checkin.api:app --host 0.0.0.0 --port 8000`
- In the app, tap **Server: … (change)** on the setup screen and type the address.
  - Same Wi-Fi as the PC: `http://<your PC's local IP>:8000` (for example `http://192.168.1.20:8000`). This test build allows plain `http://` so this works.
  - Anywhere else: run `cloudflared tunnel --url http://localhost:8000` and type the `https://…trycloudflare.com` address it prints.

## Good to know

- It's a test build signed with the standard Android debug key, so it can't go on the Play Store and a later store version will need uninstalling this one first.
- Reminders are local to the phone. Server push notifications aren't wired up yet (see `LAUNCH.md` step 3).
- Works on 64-bit and 32-bit ARM phones (nearly all real phones). It won't run on an x86 emulator.
