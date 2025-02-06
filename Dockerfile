# Base Image
FROM python:3.12-slim

# run this before copying requirements for cache efficiency
RUN pip install --upgrade pip

# Set working directory
WORKDIR /

# Adding requirements file to current directory
# just this file first to cache the pip install step when code changes
COPY requirements.txt .

#install dependencies
RUN pip install -r requirements.txt

# copy code itself from context to image
COPY . .

# Copy files
COPY . .

# Expose port
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "app.py"]