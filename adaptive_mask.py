from PIL import Image
from pathlib import Path

source = Path.home() / "storage/shared/DCIM/Camera/20261112_200137.jpg"

with Image.open(source) as photo:
    gray = photo.convert("L").resize((100, 100))

hist = gray.histogram()
total = sum(hist)
weighted = sum(i * hist[i] for i in range(256))

best = -1
threshold = 0
background_count = 0
background_sum = 0

for t in range(256):
    background_count += hist[t]
    background_sum += t * hist[t]

    foreground_count = total - background_count

    if background_count == 0 or foreground_count == 0:
        continue

    mean_background = background_sum / background_count
    mean_foreground = (weighted - background_sum) / foreground_count

    score = (
        background_count * foreground_count *
        (mean_background - mean_foreground) ** 2
    )

    if score > best:
        best = score
        threshold = t

mask = gray.point(
    lambda p: 255 if p <= threshold else 0
)

mask.resize(
    (500, 500),
    Image.Resampling.NEAREST
).save("adaptive_mask.png")

print("S-Eye: Adaptive segmentation")
print("Calculated threshold:", threshold)
print("Saved: adaptive_mask.png")
