#!/usr/bin/env bash
set -euo pipefail
apk="${1:?Provide the preview APK}"
adb install -r "$apk"
adb shell am start -W -n online.slickk.seye/.MainActivity
remote=/sdcard/seye-ui.xml
snapshot="$(mktemp)"
trap 'rm -f "$snapshot"' EXIT
adb shell uiautomator dump "$remote"
adb pull "$remote" "$snapshot"
read -r x y < <(python - "$snapshot" <<'PY'
import re
import sys
import xml.etree.ElementTree as ET

for node in ET.parse(sys.argv[1]).iter("node"):
    if node.get("text", "").lower() == "try sample":
        a, b, c, d = map(int, re.findall(r"\d+", node.attrib["bounds"]))
        print((a + c) // 2, (b + d) // 2)
        break
else:
    raise SystemExit("Could not find Try sample")
PY
)
adb shell input tap "$x" "$y"
adb shell uiautomator dump "$remote"
adb pull "$remote" "$snapshot"
python - "$snapshot" <<'PY'
import sys
import xml.etree.ElementTree as ET

assert any(node.get("text") == "Circle" for node in ET.parse(sys.argv[1]).iter("node")), "Built-in sample did not display Circle"
print("APK installed and sample classified on the Android emulator")
PY
