# Build and install the Clari Android APK

A local build: no Expo account, no EAS and no Android Studio. The output is `dist/clari-<version>.apk`, a release build signed with Clari's own release key. It runs on any Android 7+ phone (32- and 64-bit ARM), but not on an x86 emulator.

## Point it at a server (no rebuild)

The server address and access key are set inside the app, so one APK works with any server:

1. Start the server and tunnel (see `../HOME-TESTING.md`). The tunnel prints an `https://<random>.trycloudflare.com` address.
2. On the phone's first screen, tap **Server settings**.
3. Type the tunnel address. If the server has `API_TOKEN` set, type that into **Access key**.
4. Tap **Save**. The app checks that the server answers and accepts the key before saving.

Both are saved on the phone. When the tunnel address changes, go back to **Server settings** and type the new one. Release builds only allow `https://` addresses, so use the tunnel or a hosted server, not a LAN `http://` address.

## Install it

**With a USB cable (adb):** turn on Developer options and USB debugging on the phone, plug it in, then run:

```bash
~/Library/Android/sdk/platform-tools/adb install -r dist/clari-1.0.0.apk
```

`-r` updates an installed copy and keeps its data.

**Sideload:** send the `.apk` to the phone (email, Google Drive, or copy it to Downloads) and open it. Allow "install from this source" if asked. If Play Protect warns about an unknown app, tap **More details → Install anyway**.

If the phone has the older "Daily Check-in" test APK, uninstall it first. That APK was signed with a different key, so Android won't install over it.

## Rebuild it

You need a JDK 17, the Android SDK and Node 22+. On this Mac they're installed under the user folder, with no Homebrew or sudo:

| What | Where | From |
|---|---|---|
| JDK 17 (Temurin) | `~/Library/Java/JavaVirtualMachines/` | adoptium.net |
| Android SDK: cmdline-tools, platform-tools, build-tools 37.0.0, NDK 27.1.12297006, CMake 3.22.1 | `~/Library/Android/sdk` | dl.google.com |
| Node 22 | `~/.local/share/node/current` | nodejs.org |

On a fresh Mac, unpack the cmdline-tools zip to `~/Library/Android/sdk/cmdline-tools/latest`, then run:

```bash
~/Library/Android/sdk/cmdline-tools/latest/bin/sdkmanager --licenses
```

```bash
~/Library/Android/sdk/cmdline-tools/latest/bin/sdkmanager "platform-tools" "build-tools;37.0.0" "ndk;27.1.12297006" "cmake;3.22.1"
```

Gradle fetches the Android platform itself.

Then, from `daily-checkin/app`:

```bash
./scripts/build-android.sh
```

The script runs `expo prebuild -p android` (which regenerates the ignored `android/` folder) and `gradlew assembleRelease`, then copies the APK to `dist/`. The first build takes about 20 minutes and later builds take a few. It caps Gradle at 3 workers and lowers its priority so the Mac stays usable.

- **Version:** raise `expo.version` and `expo.android.versionCode` in `app.json` before building an update that should install over the last one.
- **Release key:** the first run creates `~/.clari-android/release.jks`, with its password in `~/.clari-android/signing.env`. Both live outside the repo and must never be committed. Back the folder up: Android only installs an update that's signed with the same key. If the key is lost, testers have to uninstall and reinstall.
- **Debug key instead:** `./scripts/build-android.sh --debug` signs with the shared Expo debug key.
- **Built-in defaults:** setting `EXPO_PUBLIC_API_URL` or `EXPO_PUBLIC_API_TOKEN` while building only changes the defaults the app starts with. Leave the token unset for APKs you share, so it isn't baked into the file, and have testers type it into **Server settings** instead.
