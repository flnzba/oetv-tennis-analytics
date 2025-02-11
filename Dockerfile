# Base Image
FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# run this before copying requirements for cache efficiency
RUN pip install --upgrade pip

# Set working directory
WORKDIR /scripts

# Adding requirements file to current directory
# just this file first to cache the pip install step when code changes
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy code itself from context to image
COPY . .

# Expose port
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Command to run the app
ENTRYPOINT ["streamlit", "run", "scripts/app.py", "--server.port=8501", "--server.address=0.0.0.0"]