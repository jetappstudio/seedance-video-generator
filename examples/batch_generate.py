#!/usr/bin/env python3
"""Batch: Multiple images → multiple videos"""

from seedance_video import image_to_video
import os
import glob

PROMPTS = {
    "product": "elegant product showcase, studio lighting, smooth droning camera, dark background",
    "food": "delicious food close-up, appetizing, steam rising, warm lighting",
    "nature": "cinematic nature scene, golden hour, peaceful atmosphere",
    "portrait": "cinematic portrait, natural lighting, shallow depth of field",
}

IMAGE_DIR = "examples/images"  # <-- תיקייה עם תמונות
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

images = glob.glob(os.path.join(IMAGE_DIR, "*.jpg")) + 
         glob.glob(os.path.join(IMAGE_DIR, "*.png"))

print(f"🎬 Batch Generation: {len(images)} images")
print()

for i, img_path in enumerate(images, 1):
    name = os.path.splitext(os.path.basename(img_path))[0]
    prompt = PROMPTS.get(name, "cinematic, professional quality")
    
    print(f"[{i}/{len(images)}] Processing: {name}")
    try:
        video_url, out_path = image_to_video(
            image_path=img_path,
            prompt=prompt,
            duration=10,
        )
        print(f"      ✅ {out_path}")
    except Exception as e:
        print(f"      ❌ Error: {e}")
    print()

print("🎉 Batch complete!")
