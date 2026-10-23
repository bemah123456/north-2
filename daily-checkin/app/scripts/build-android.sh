#!/usr/bin/env bash
# Builds a signed release APK of Clari into dist/. See BUILD-ANDROID.md.
#
#   scripts/build-android.sh            # release APK, signed with your release key
#   scripts/build-android.sh --debug    # release APK, signed with the shared debug key
#
# The server address and access key are typed into the app's "Server settings",
# so one APK works with any server. EXPO_PUBLIC_API_URL / EXPO_PUBLIC_API_TOKEN,
# if set, only change the built-in defaults.
set -euo pipefail

cd "$(dirname "$0")/.."
APP_DIR=$(pwd)

export JAVA_HOME=${JAVA_HOME:-$(/usr/libexec/java_home -v 17)}
export ANDROID_HOME=${ANDROID_HOME:-$HOME/Library/Android/sdk}
[ -d "$HOME/.local/share/node/current/bin" ] && export PATH="$HOME/.local/share/node/current/bin:$PATH"
export PATH="$ANDROID_HOME/platform-tools:$PATH"

# The release key lives outside the repo. Phones only accept an update signed
# with the same key, so back this folder up; losing it means testers have to
# uninstall before installing a newer build.
KEY_DIR=${CLARI_KEY_DIR:-$HOME/.clari-android}
KEYSTORE="$KEY_DIR/release.jks"
SIGNING="$KEY_DIR/signing.env"

if [ "${1:-}" != "--debug" ] && [ ! -f "$KEYSTORE" ]; then
  echo "No release key yet; making one in $KEY_DIR"
  mkdir -p "$KEY_DIR" && chmod 700 "$KEY_DIR"
  PASS=$(openssl rand -base64 24 | tr -d '/+=')
  keytool -genkeypair -v -keystore "$KEYSTORE" -alias clari -keyalg RSA -keysize 2048 -validity 10000 \
    -storepass "$PASS" -keypass "$PASS" -dname "CN=Clari, O=North 2" >/dev/null
  printf 'CLARI_STORE_PASSWORD=%s\n' "$PASS" > "$SIGNING"
  chmod 600 "$KEYSTORE" "$SIGNING"
fi

[ -d node_modules ] || npm ci --no-audit --no-fund
# Prebuild rewrites the run scripts in package.json; put them back after.
PKG=$(mktemp) && cp package.json "$PKG"
CI=1 npx expo prebuild -p android --no-install
cp "$PKG" package.json && rm "$PKG"

GRADLE_ARGS=(
  assembleRelease
  --max-workers=3                                     # keeps the Mac usable
  -PreactNativeArchitectures=armeabi-v7a,arm64-v8a    # real phones only; halves the size
)
if [ "${1:-}" != "--debug" ]; then
  # shellcheck disable=SC1090
  source "$SIGNING"
  GRADLE_ARGS+=(
    -Pandroid.injected.signing.store.file="$KEYSTORE"
    -Pandroid.injected.signing.store.password="$CLARI_STORE_PASSWORD"
    -Pandroid.injected.signing.key.alias=clari
    -Pandroid.injected.signing.key.password="$CLARI_STORE_PASSWORD"
  )
fi

(cd android && nice -n 10 ./gradlew "${GRADLE_ARGS[@]}")

VERSION=$(node -p "require('./app.json').expo.version")
mkdir -p dist
OUT="dist/clari-$VERSION.apk"
cp android/app/build/outputs/apk/release/app-release.apk "$OUT"
"$ANDROID_HOME/build-tools/37.0.0/apksigner" verify --print-certs "$OUT" | grep -m1 "certificate SHA-256" || true
echo "Built $APP_DIR/$OUT ($(du -h "$OUT" | cut -f1))"
