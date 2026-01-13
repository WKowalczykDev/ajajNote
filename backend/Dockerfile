FROM python:3.13-slim

WORKDIR /app

# Instalacja zależności systemowych (np. gcc dla niektórych bibliotek pythona)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy kod
COPY . .

# Ustawiamy zmienną środowiskową wskazującą, gdzie są dane
ENV UPLOAD_FOLDER=/app/data

# Port Flask
EXPOSE 5000

# Uruchomienie (zalecane użycie gunicorn na produkcji, tu dla dev flask run)
CMD ["python", "init.py"]
# Lub jeśli używasz create_app pattern:
# CMD ["flask", "run", "--host=0.0.0.0"]