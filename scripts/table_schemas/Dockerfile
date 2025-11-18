# Use official lightweight Python 3.10 image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /table_schemas

# Ensure Python behaves predictably
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system utilities (for debugging / editing)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        vim \
        less \
        curl \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy requirement file first for layer caching
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy your app source code
COPY . /table_schemas

# Keep container in interactive mode by default
CMD ["/bin/bash"]
