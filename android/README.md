# S-Eye Android preview

Version **0.3.0-preview** runs offline. Choose an image, take a photo with the
system camera app, or tap **Try sample**. The app recognizes one high-contrast
circle, triangle, or quadrilateral or returns Unknown. It supports both light
and dark backgrounds. The camera supplies a thumbnail without granting S-Eye
direct camera access or broad file permissions.

Tap **Save observation JSON** to export the result and source fingerprint.
See the [Android integration contract](../docs/ANDROID_INTEGRATION.md).

## Install

Download the APK from the **S-Eye-Android-preview** artifact of the Android
workflow. Open it on your phone and confirm installation. Android 8 is the
minimum and Android 16 is the target. From a connected computer:

    adb install path/to/S-Eye-0.3.0-preview.apk

Version 0.2.0 used a temporary signing certificate. Uninstall that preview
before installing 0.3.0 if Android rejects the update. Use the same signing
certificate for future in-place upgrades. For an owner-controlled key, the build
script accepts **SEYE_SIGNING_KEYSTORE**, **SEYE_SIGNING_ALIAS**, and
**SEYE_SIGNING_PASSWORD** as local environment variables. Keep the key outside
the repository. Unconfigured builds use a temporary preview certificate.

## Build and test

Use JDK 17, Android SDK platform 36, and Build Tools 36.0.0:

    bash android/build-apk.sh build/android
    python android/verify/benchmark.py --output build/android/recognition.json

The benchmark checks six generated held-out images, their inverted variants,
and three negative controls. The inverse-polarity variations come from the same
test images. The emulator test covers installation, the built-in sample, and
export button availability. Generalization to real photos remains unverified.
