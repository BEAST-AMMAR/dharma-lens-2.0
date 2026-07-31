FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Tesseract OCR & FFmpeg for audio/document AI
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
