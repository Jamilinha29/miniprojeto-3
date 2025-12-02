FROM python:3.11-slim
WORKDIR /app

# Install system deps for matplotlib if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libatlas-base-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./src/main.py"]
