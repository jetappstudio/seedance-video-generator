# 🎬 Seedance Video Generator

Image-to-Video & Text-to-Video powered by ByteDance Seedance 2.0

## Quick Start

```bash
source venv/bin/activate
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY
python seedance_video.py image-to-video --image your-photo.jpg --prompt "cinematic product demo"
```

## Features

- **Image-to-Video**: תמונה אחת → סרטון עד 15 שניות
- **Text-to-Video**: טקסט בלבד → סרטון
- **Two models**: `seedance-2.0` (איכות מלאה) או `seedance-2.0-fast` (מהיר, זול)
- **Powered by OpenRouter** — API key אחד, חיוב מאוחד

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Examples

```python
# Image to Video
python seedance_video.py image-to-video \\
    --image product.jpg \\
    --prompt "elegant product showcase, smooth droning light, black background" \\
    --duration 15

# Text only
python seedance_video.py text-to-video \\
    --prompt "cinematic timelapse of Tel Aviv beach at sunset, golden hour" \\
    --duration 15

# Fast mode (cheaper)
python seedance_video.py i2v -i photo.jpg -p "smooth camera pan" --duration 10 --fast
```
