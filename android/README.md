# S-Eye Android preview

This native Android app analyzes one selected image on the device. It looks
for a single dark circle, triangle, or quadrilateral against a light background.
An unsupported image may return Unknown. The preview has no internet or storage
permissions and uses Android's system document picker. It also has a built-in
circle to try without an image file.

Download the **S-Eye-Android-preview** artifact from a successful Android
preview workflow run. Extract the ZIP, open **S-Eye-0.2.0-preview.apk** on the phone,
and follow Android's installation prompt. Open S-Eye and tap **Try sample**.
The preview supports Android 8 and later. The target is Android 16.

For a connected test device, use `adb install path/to/S-Eye-0.2.0-preview.apk`.
CI uses a temporary preview certificate. Builds from different runs cannot
update one another in place. Stable updates require a persistent signing key.

Build with JDK 17 and Android SDK platform 36 and Build Tools 36.0.0:

```sh
bash android/build-apk.sh build/android
python android/verify/benchmark.py --output build/android/recognition.json
```

The Java recognizer is scoped to high-contrast shape geometry. The benchmark
reuses the Stage 199 generated test split and adds blank, clipped, and cross
controls. It does not measure representative photographs, OCR, live camera
feeds, or general object recognition. The learned Python models and their
historical benchmarks remain available as comparators.
