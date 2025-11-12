# Use an official Python slim base
FROM python:3.11-slim

# Install system packages: poppler (pdf2image), tesseract (OCR) and image deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    libsm6 libxext6 libxrender1 build-essential \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port (Render sets PORT env)
EXPOSE 8000

# Use gunicorn + uvicorn worker; Render injects $PORT at runtime
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:$PORT", "--workers", "1", "--timeout", "120"]
