#!/usr/bin/env bash

# 🧱 Ensure system packages are ready
apt-get update

# 🎬 Install FFmpeg for audio/video processing
apt-get install -y ffmpeg

# 📦 Install Python dependencies
pip install -r requirements.txt
# pip install --no-cache-dir -r requirements.txt


