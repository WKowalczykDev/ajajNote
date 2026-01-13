FROM python:3.13-slim

WORKDIR /app

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tworzymy katalog database wewnątrz kontenera
RUN mkdir -p /app/database

COPY . .

# Aktualizujemy domyślne zmienne (zostaną i tak nadpisane przez docker-compose, ale dla porządku)
ENV UPLOAD_FOLDER=/app/database/Users

EXPOSE 5000

CMD ["python", "init.py"]