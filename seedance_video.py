#!/usr/bin/env python3
"""
Seedance Video Generator
Image-to-Video & Text-to-Video using ByteDance Seedance 2.0
via muapi.ai API
"""

import os
import sys
import time
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MUAPI_API_KEY = os.getenv("MUAPI_API_KEY")
if not MUAPI_API_KEY:
    print("❌ MUAPI_API_KEY not found! Set it in .env file.")
    print("   Get your free key at https://muapi.ai")
    sys.exit(1)

MUAPI_BASE = "https://api.muapi.ai/api/v1/seedance"


def upload_image(image_path: str, api_key: str) -> str:
    """Upload local image and return URL."""
    url = "https://api.muapi.ai/api/v1/image/nowater"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        resp = requests.post(url, headers=headers, files=files)
    
    resp.raise_for_status()
    data = resp.json()
    image_url = data.get("data", {}).get("imageUrl") or data.get("imageUrl")
    if not image_url:
        raise Exception(f"Upload failed: {data}")
    return image_url


def submit_task(api_key: str, payload: dict) -> str:
    """Submit generation task, return task_id."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    url = f"{MUAPI_BASE}/text2video"
    
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    
    task_id = data.get("data", {}).get("taskId") or data.get("taskId")
    if not task_id:
        raise Exception(f"Submit failed: {json.dumps(data, indent=2)}")
    return task_id


def check_result(api_key: str, task_id: str) -> dict:
    """Check task status."""
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{MUAPI_BASE}/task?taskId={task_id}"
    
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def wait_for_completion(api_key: str, task_id: str, max_wait: int = 600) -> str:
    """Poll until task completes, return video URL."""
    print(f"⏳ Task submitted: {task_id}")
    print(f"   Checking status every 10s (max {max_wait}s)...")
    
    for i in range(max_wait // 10):
        time.sleep(10)
        result = check_result(api_key, task_id)
        
        status = result.get("data", {}).get("status") or result.get("status")
        
        if status == "COMPLETED":
            video_url = (result.get("data", {}).get("videoUrl") or 
                        result.get("videoUrl") or
                        (result.get("data", {}).get("result", {}).get("videoUrl")))
            if video_url:
                return video_url
            # Try to find URL in nested response
            print(f"   Response: {result}")
            return str(result)
        
        elif status == "FAILED":
            raise Exception(f"Task failed: {result}")
        
        elapsed = (i + 1) * 10
        print(f"   [{elapsed}s] Status: {status or 'processing'}...")
    
    raise TimeoutError(f"Task did not complete in {max_wait}s")


def download_video(video_url: str, output_path: str):
    """Download generated video."""
    print(f"📥 Downloading video...")
    resp = requests.get(video_url, stream=True)
    resp.raise_for_status()
    
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"✅ Video saved: {output_path}")


def image_to_video(image_path: str, prompt: str, duration: int = 10, 
                   camera: str = "fixed", output: str = "output"):
    """Generate video from image."""
    os.makedirs(output, exist_ok=True)
    
    print(f"📤 Uploading image: {image_path}")
    image_url = upload_image(image_path, MUAPI_API_KEY)
    print(f"   Image URL: {image_url}")
    
    payload = {
        "prompt": prompt,
        "image": image_url,
        "duration": duration,
        "cameraType": camera,
    }
    
    task_id = submit_task(MUAPI_API_KEY, payload)
    video_url = wait_for_completion(MUAPI_API_KEY, task_id)
    
    print(f"✅ Video generated!")
    print(f"   URL: {video_url}")
    
    # Download
    ts = int(time.time())
    out_file = os.path.join(output, f"video_{ts}.mp4")
    download_video(video_url, out_file)
    
    return video_url, out_file


def text_to_video(prompt: str, duration: int = 10, camera: str = "fixed", output: str = "output"):
    """Generate video from text only."""
    os.makedirs(output, exist_ok=True)
    
    payload = {
        "prompt": prompt,
        "duration": duration,
        "cameraType": camera,
    }
    
    task_id = submit_task(MUAPI_API_KEY, payload)
    video_url = wait_for_completion(MUAPI_API_KEY, task_id)
    
    print(f"✅ Video generated!")
    print(f"   URL: {video_url}")
    
    ts = int(time.time())
    out_file = os.path.join(output, f"video_{ts}.mp4")
    download_video(video_url, out_file)
    
    return video_url, out_file


def main():
    parser = argparse.ArgumentParser(description="🎬 Seedance Video Generator")
    sub = parser.add_subparsers(dest="command")
    
    # Image-to-video
    img_parser = sub.add_parser("image-to-video", aliases=["i2v"], help="תמונה → סרטון")
    img_parser.add_argument("--image", "-i", required=True, help="נתיב לתמונה")
    img_parser.add_argument("--prompt", "-p", required=True, help="תיאור הסרטון")
    img_parser.add_argument("--duration", "-d", type=int, default=10, help="אורך בשניות (5-15)")
    img_parser.add_argument("--camera", "-c", default="fixed", 
                           fixed="fixed", slow_pan_right="slow_pan_right",
                           slow_pan_left="slow_pan_left", slow_zoom_in="slow_zoom_in",
                           slow_zoom_out="slow_zoom_out", handheld="handheld")
    img_parser.add_argument("--output", "-o", default="output")
    
    # Text-to-video
    txt_parser = sub.add_parser("text-to-video", aliases=["t2v"], help="טקסט → סרטון")
    txt_parser.add_argument("--prompt", "-p", required=True, help="תיאור הסרטון")
    txt_parser.add_argument("--duration", "-d", type=int, default=10, help="אורך בשניות (5-15)")
    txt_parser.add_argument("--camera", "-c", default="fixed")
    txt_parser.add_argument("--output", "-o", default="output")
    
    args = parser.parse_args()
    
    if args.command in ("image-to-video", "i2v"):
        image_to_video(args.image, args.prompt, args.duration, args.camera, args.output)
    elif args.command in ("text-to-video", "t2v"):
        text_to_video(args.prompt, args.duration, args.camera, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    import json  # needed for error formatting
    main()
