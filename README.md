# 🎬 Seedance Video Generator

Image-to-Video & Text-to-Video powered by ByteDance Seedance 2.0

## Quick Start

```bash
source venv/bin/activate
cp .env.example .env
# Edit .env with your MUAPI_API_KEY
python seedance_video.py image-to-video --image your-photo.jpg --prompt "cinematic product demo"
```

## Features

- **Image-to-Video**: תמונה אחת → סרטון עד 15 שניות
- **Text-to-Video**: טקסט בלבד → סרטון
- **Camera Controls**: pan, zoom, rotate, handheld
- **Multi-Reference**: עד 9 תמונות כרפרנס
- **Audio Sync**: סנכרון סאונד לסרטון

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## API Key

צריך API key דרך [muapi.ai](https://muapi.ai) — נקודות חינמיות להתחלה.

## Examples

```python
# Image to Video with camera motion
python seedance_video.py image-to-video \
    --image product.jpg \
    --prompt "elegant product showcase, smooth droning light, black background" \
    --camera slow_zoom_in \
    --duration 10

# Text only
python seedance_video.py text-to-video \
    --prompt "cinematic timelapse of Tel Aviv beach at sunset, golden hour" \
    --duration 15
```
