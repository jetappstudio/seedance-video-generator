#!/usr/bin/env python3
"""
Seedance Video Generator
Image-to-Video & Text-to-Video using ByteDance Seedance 2.0
via OpenRouter API (https://openrouter.ai)
"""

import os
import sys
import time
import json
import argparse
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("❌ OPENROUTER_API_KEY not found! Set it in .env file.")
    sys.exit(1)

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
MODEL = "bytedance/seedance-2.0"  # or "bytedance/seedance-2.0-fast"


def image_to_base64(image_path: str) -> str:
    """Convert local image to base64 data URL."""
    import mimetypes
    mime, _ = mimetypes.guess_type(image_path)
    mime = mime or "image/jpeg"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def submit_video_task(
    api_key: str,
    prompt: str,
    image_url: str = None,
    duration: int = 10,
    fast: bool = False,
) -> str:
    """Submit video generation task, return generation_id."""
    model = "bytedance/seedance-2.0-fast" if fast else "bytedance/seedance-2.0"
    
    url = f"{OPENROUTER_BASE}/videos"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Build prompt with image reference if provided
    full_prompt = prompt
    if image_url:
        full_prompt = f"Generate a video based on this reference image. {prompt}"
    
    payload = {
        "prompt": full_prompt,
        "model": model,
    }
    
    # Add image if provided (base64 data URL)
    if image_url:
        if image_url.startswith("data:"):
            payload["image"] = image_url
        elif image_url.startswith("http"):
            payload["image"] = image_url
    
    print(f"📤 Submitting task to OpenRouter...")
    print(f"   Model: {model}")
    print(f"   Prompt: {prompt[:80]}...")
    
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    
    if resp.status_code != 200:
        print(f"❌ Error response: {resp.text[:500]}")
    resp.raise_for_status()
    
    data = resp.json()
    # OpenRouter returns generation_id in response
    gen_id = (
        data.get("id")
        or data.get("data", {}).get("id")
        or data.get("generation_id")
    )
    
    if not gen_id:
        raise Exception(f"Unexpected response: {json.dumps(data, indent=2)}")
    
    return gen_id


def poll_generation(api_key: str, generation_id: str, timeout: int = 600) -> dict:
    """Poll OpenRouter for video generation result."""
    url = f"{OPENROUTER_BASE}/videos/{generation_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    print(f"⏳ Polling generation: {generation_id}")
    start = time.time()
    
    while time.time() - start < timeout:
        resp = requests.get(url, headers=headers, timeout=30)
        data = resp.json()
        
        # Extract response data
        result = data.get("data", data)
        status = result.get("status", result.get("state", "unknown"))
        
        if status in ("completed", "success", "finished"):
            return result
        elif status in ("failed", "error"):
            raise Exception(f"Generation failed: {json.dumps(data, indent=2)}")
        
        elapsed = int(time.time() - start)
        print(f"   [{elapsed}s] Status: {status}...")
        time.sleep(15)
    
    raise TimeoutError(f"Generation did not complete in {timeout}s")


def extract_video_url(result: dict) -> str:
    """Extract video URL from OpenRouter response."""
    # Try various response formats
    url = (
        result.get("video_url")
        or result.get("url")
        or result.get("output", {}).get("url")
        or result.get("data", {}).get("video_url")
    )
    
    if not url:
        # Sometimes the video is in artifacts or outputs
        outputs = result.get("outputs", result.get("artifacts", []))
        if isinstance(outputs, dict):
            outputs = outputs.values()
        if isinstance(outputs, list):
            for item in outputs:
                if isinstance(item, str) and item.endswith((".mp4", ".webm")):
                    url = item
                    break
    
    return url


def download_video(video_url: str, output_path: str):
    """Download generated video."""
    print(f"📥 Downloading video...")
    resp = requests.get(video_url, stream=True, timeout=120)
    resp.raise_for_status()
    
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"✅ Video saved: {output_path}")


def image_to_video(
    image_path: str,
    prompt: str,
    duration: int = 10,
    fast: bool = False,
    output: str = "output",
):
    """Generate video from image."""
    os.makedirs(output, exist_ok=True)
    
    print(f"📸 Converting image to base64: {image_path}")
    image_b64 = image_to_base64(image_path)
    
    gen_id = submit_video_task(
        OPENROUTER_API_KEY, prompt,
        image_url=image_b64, duration=duration, fast=fast
    )
    
    result = poll_generation(OPENROUTER_API_KEY, gen_id)
    video_url = extract_video_url(result)
    
    if video_url:
        print(f"✅ Video generated!")
        print(f"   URL: {video_url}")
        ts = int(time.time())
        out_file = os.path.join(output, f"video_{ts}.mp4")
        download_video(video_url, out_file)
        return video_url, out_file
    else:
        print(f"⚠️  No video URL in response. Full result:")
        print(json.dumps(result, indent=2, default=str))
        return None, None


def text_to_video(prompt: str, duration: int = 10, fast: bool = False, output: str = "output"):
    """Generate video from text only."""
    os.makedirs(output, exist_ok=True)
    
    gen_id = submit_video_task(OPENROUTER_API_KEY, prompt, duration=duration, fast=fast)
    result = poll_generation(OPENROUTER_API_KEY, gen_id)
    video_url = extract_video_url(result)
    
    if video_url:
        print(f"✅ Video generated!")
        print(f"   URL: {video_url}")
        ts = int(time.time())
        out_file = os.path.join(output, f"video_{ts}.mp4")
        download_video(video_url, out_file)
        return video_url, out_file
    else:
        print(f"⚠️  No video URL in response. Full result:")
        print(json.dumps(result, indent=2, default=str))
        return None, None


def main():
    parser = argparse.ArgumentParser(description="🎬 Seedance Video Generator (via OpenRouter)")
    sub = parser.add_subparsers(dest="command")

    # Image-to-video
    img_parser = sub.add_parser("image-to-video", aliases=["i2v"], help="תמונה → סרטון")
    img_parser.add_argument("--image", "-i", required=True, help="נתיב לתמונה")
    img_parser.add_argument("--prompt", "-p", required=True, help="תיאור הסרטון")
    img_parser.add_argument("--duration", "-d", type=int, default=10, help="אורך בשניות (5-15)")
    img_parser.add_argument("--fast", action="store_true", help="השתמש בגרסה המהירה (זולה יותר)")
    img_parser.add_argument("--output", "-o", default="output")

    # Text-to-video
    txt_parser = sub.add_parser("text-to-video", aliases=["t2v"], help="טקסט → סרטון")
    txt_parser.add_argument("--prompt", "-p", required=True, help="תיאור הסרטון")
    txt_parser.add_argument("--duration", "-d", type=int, default=10, help="אורך בשניות (5-15)")
    txt_parser.add_argument("--fast", action="store_true", help="השתמש בגרסה המהירה (זולה יותר)")
    txt_parser.add_argument("--output", "-o", default="output")

    args = parser.parse_args()

    if args.command in ("image-to-video", "i2v"):
        image_to_video(args.image, args.prompt, args.duration, fast=args.fast, output=args.output)
    elif args.command in ("text-to-video", "t2v"):
        text_to_video(args.prompt, args.duration, fast=args.fast, output=args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
