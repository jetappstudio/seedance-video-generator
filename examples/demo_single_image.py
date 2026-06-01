#!/usr/bin/env python3
"""Demo: Single Image → 15s Video"""

from seedance_video import image_to_video, upload_image
import os

IMAGE = "examples/sample.jpg"  # <-- שם/נתיב של התמונה שלך
PROMPT = "cinematic product showcase, elegant lighting, smooth camera movement, black background"
DURATION = 15

print("🎬 Seedance Image-to-Video Demo")
print(f"   Image: {IMAGE}")
print(f"   Prompt: {PROMPT}")
print(f"   Duration: {DURATION}s")
print()

video_url, output_path = image_to_video(
    image_path=IMAGE,
    prompt=PROMPT,
    duration=DURATION,
    camera="slow_zoom_in",
)

print(f"\n🎉 Done!")
print(f"   Video URL: {video_url}")
print(f"   Saved to: {output_path}")
