# ✅ Use official Python 3.13 image
FROM python:3.13.2-slim

# 🧱 Set working directory
WORKDIR /app

# 🧱 Copy everything
COPY . .

# 📦 Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# 📦 Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 🌐 Expose port (use 10000 as per your setup)
EXPOSE 10000

# ✅ Automatically detect PORT from environment (Render) or default to 10000
ENV PORT=10000

# 🚀 Start FastAPI with uvicorn
CMD ["python", "-c", "import os; import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=int(os.getenv('PORT', 10000)), log_level='debug')"]
