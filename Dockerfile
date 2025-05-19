# Use slim image for smaller size
FROM python:3.11-slim

# -----------------------------
# 1. System-level dependencies
# -----------------------------
RUN apt-get update && apt-get install -y ffmpeg

# -----------------------------
# 2. Set work directory
# -----------------------------
WORKDIR /app

# -----------------------------
# 3. Install Python packages
# -----------------------------
COPY requirements.txt .
RUN pip install --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir --prefer-binary -r requirements.txt
# Install Python packages (CPU-only PyTorch)
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# -----------------------------
# 4. Copy application code
# -----------------------------
COPY . .

# -----------------------------
# 5. Pre-download Whisper model
# -----------------------------
RUN python -c "import whisper; whisper.load_model('base')"
# RUN python -c "import whisper; whisper.load_model('medium')"

# -----------------------------
# 6. Start FastAPI server
# -----------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
