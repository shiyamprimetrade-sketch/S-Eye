# Android observation integration

1. Analyze an image or try the built-in sample in S-Eye Android.
2. Tap **Save observation JSON** and choose a document location.
3. Transfer the JSON to a directory that S-Eye is allowed to read.
4. Validate it locally. For a selected document, you can also supply the exact
   original file using **--image**.

    seye-local --root /path/to/inbox android-report --report /path/to/inbox/seye-observation.json

S can call the same adapter through **seye-workflow --strict** and the existing
read and output filesystem grants, using the following JSON request.

    {
      "schema_version": 1,
      "request_id": "android-001",
      "action": "android_observation",
      "report": "/path/to/inbox/seye-observation.json",
      "image": "/path/to/inbox/original.png"
    }

| Report field | Meaning |
| --- | --- |
| **format**, **schema_version** | Fixed identifiers seye-android-observation-v1 and 1. |
| **app_version** | Android build version. |
| **source_kind** | document, sample, or camera_thumbnail. |
| **sha256**, **source_bytes** | Fingerprint and length of the original selected bytes or the PNG encoding generated in memory for samples and camera thumbnails. |
| **analyzed_size** | Width and height after decoding or downsampling. |
| **label**, **accepted** | Geometry hypothesis and whether the recognizer accepted it. |

With matching image bytes, **source_bytes_match** is true. A mismatch produces a
typed failure. If the optional image is omitted, **source_bytes_match** is null.
Label accuracy is unverified and **classification_verified** is always false.
The adapter reads only caller-selected files within its read roots.
Android transfers nothing automatically. Deployment in the parent S repository
remains open.
