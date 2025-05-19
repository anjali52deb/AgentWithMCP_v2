# ✅ Use official Python 3.13 slim image
FROM python:3.13.2-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# 🔧 Install required system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    build-essential \
    && apt-get clean

# 🐍 Upgrade pip and install Python deps (except Whisper)
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 🦀 Install Rust (required for Whisper build)
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y \
 && export PATH="$HOME/.cargo/bin:$PATH" \
 && pip install --no-cache-dir git+https://github.com/openai/whisper.git

# 🌐 Expose the app port
EXPOSE 10000

# Set environment variable for Render compatibility
ENV PORT=10000

# 🏁 Run the FastAPI app using uvicorn
CMD ["python", "-c", "import os; import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=int(os.getenv('PORT', 10000)), log_level='debug')"]
