FROM python:3.13-slim

# Install Tesseract OCR and dependencies
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev pkg-config

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . /app
WORKDIR /app

# Expose the port Streamlit will run on (Render default 10000 or specify your own)
EXPOSE 10000

# Run the Streamlit app (adjust app.py if needed)
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]
