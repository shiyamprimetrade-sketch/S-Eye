#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
sdk="${ANDROID_SDK_ROOT:-${ANDROID_HOME:?Set ANDROID_HOME to your Android SDK}}"
tools="$sdk/build-tools/36.0.0"
platform="$sdk/platforms/android-36/android.jar"
output="${1:?Provide an output directory}"
mkdir -p "$output"
output="$(cd -- "$output" && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/classes" "$work/dex"

javac -encoding UTF-8 --release 8 -classpath "$platform" \
    -d "$work/classes" "$root"/src/online/slickk/seye/*.java
jar cf "$work/classes.jar" -C "$work/classes" .
"$tools/d8" --min-api 26 --lib "$platform" --output "$work/dex" "$work/classes.jar"
"$tools/aapt2" link -I "$platform" --manifest "$root/AndroidManifest.xml" -o "$work/base.apk"
zip -q -j -0 "$work/base.apk" "$work/dex/classes.dex"
"$tools/zipalign" -f 4 "$work/base.apk" "$work/aligned.apk"

apk="$output/S-Eye-0.3.0-preview.apk"
if [[ -n "${SEYE_SIGNING_KEYSTORE:-}" ]]; then
    : "${SEYE_SIGNING_ALIAS:?Set the signing alias}"
    : "${SEYE_SIGNING_PASSWORD:?Set the keystore password}"
    export SEYE_SIGNING_PASSWORD
    "$tools/apksigner" sign --ks "$SEYE_SIGNING_KEYSTORE" --ks-key-alias "$SEYE_SIGNING_ALIAS" \
        --ks-pass env:SEYE_SIGNING_PASSWORD --out "$apk" "$work/aligned.apk"
else
    keytool -genkeypair -noprompt -keystore "$work/preview.p12" -storepass android \
        -alias seye-preview -dname 'CN=S-Eye Android Preview' -keyalg RSA -keysize 2048 -validity 10000
    "$tools/apksigner" sign --ks "$work/preview.p12" --ks-pass pass:android --out "$apk" "$work/aligned.apk"
fi
"$tools/apksigner" verify --verbose --print-certs "$apk" > "$output/signature.txt"
"$tools/aapt2" dump badging "$apk" > "$output/package.txt"
(cd "$output" && sha256sum "$(basename "$apk")" > SHA256SUMS)
