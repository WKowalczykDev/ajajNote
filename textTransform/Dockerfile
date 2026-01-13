FROM python:3.13-slim

WORKDIR /app

# ffmpeg jest często potrzebny do obróbki audio
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATA_DIR=/app/data

EXPOSE 5001

CMD ["python", "main.py"]