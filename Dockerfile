# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies required for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and system dependencies
# This is crucial for the scraper to work in the container
RUN playwright install --with-deps chromium

# Copy project
COPY . /app/

# Expose the port the app runs on
EXPOSE 5000

# Run the application using Gunicorn
# Adjust workers and timeout as needed. 
# Timeout is set to 120s to allow for scraping operations
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "app.main:app"]
