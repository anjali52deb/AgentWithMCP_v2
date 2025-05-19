# ✅ Use official Python 3.13 slim image
FROM python:3.13.2-slim

# Set working directory
WORKDIR /app

# Copy all source files
COPY . .

# 🧱 Install system-level dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    build-essential \
    && apt-get clean

# ✅ Install pip dependencies (except whisper and torch)
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ✅ Install CPU-only PyTorch explicitly (before whisper)
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# ✅ Install Whisper from GitHub (latest version)
RUN pip install --no-cache-dir git+https://github.com/openai/whisper.git

# 🔓 Expose application port
EXPOSE 10000

# 🌐 Support Render or default local port
ENV PORT=10000

# 🏁 Run FastAPI using uvicorn
CMD ["python", "-c", "import os; import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=int(os.getenv('PORT', 10000)), log_level='debug')"]
