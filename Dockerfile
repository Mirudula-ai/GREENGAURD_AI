# Use official Python 3.10 slim image
FROM python:3.10-slim

# Install system dependencies needed for Tesseract OCR and Pillow
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Upgrade pip, setuptools, wheel to latest versions for smooth installs
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire app code
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Run the Streamlit app on Render’s dynamic port
CMD streamlit run app.py --server.port=8501 --server.address=0.0.0.0
