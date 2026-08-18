FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libxcb1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p uploads output/jobs

EXPOSE 10000

CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}