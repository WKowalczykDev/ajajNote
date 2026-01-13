FROM python:3.13-slim

WORKDIR /app

# Instalacja zależności systemowych (np. gcc)
# Jest to często wymagane do kompilacji niektórych bibliotek pythona
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy kod
COPY . .

# Ustawiamy zmienną środowiskową wskazującą, gdzie są dane
ENV UPLOAD_FOLDER=/app/data

# Port Flask
EXPOSE 5000

# Uruchomienie
CMD ["python", "init.py"]