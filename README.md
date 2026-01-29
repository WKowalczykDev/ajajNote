# AINote

Automatyczne tworzenie notatek z nagrań audio przy użyciu AI (AssemblyAI + Gemini 2.5 Pro).

## Wymagania

- Docker & Docker Compose
- Klucze API:
  - [AssemblyAI](https://www.assemblyai.com/) (darmowy - 50$ darmowych kredytów)
  - [Google Gemini](https://ai.google.dev/) (pro dla studentów za darmo)

## Instalacja

1. **Sklonuj repozytorium**
```bash
git clone <repository-url>
cd ainote
```

2. **Utwórz plik `.env` w katalogu głównym**
```bash
ASSEMBLYAI_API_KEY=your_assemblyai_key
GOOGLE_API_KEY=your_google_key
ADMIN_PASSWORD=admin123
SECRET_KEY=your_secret_key_here
```

3. **Uruchom aplikację**
```bash
docker-compose up --build
```

4. **Otwórz w przeglądarce**
```
http://localhost:5173
```

## Jak używać

1. Zarejestruj konto lub zaloguj się
2. Przeciągnij plik audio (MP3, WAV) lub nagraj przez mikrofon
3. Kliknij na notatkę i wybierz **Process Note**
4. Po ~30s-5 min eksportuj do PDF

## Struktura projektu
```
ainote/
├── backend/          # Flask API (autentykacja, baza danych)
├── frontend/         # React UI
├── textTransform/    # Mikroserwis transkrypcji (AssemblyAI + Gemini)
├── database/         # SQLite + pliki użytkowników (auto-tworzone)
└── docker-compose.yml
```

## Technologie

- **Transkrypcja**: AssemblyAI (Speaker Diarization)
- **Analiza**: Google Gemini 2.5 Pro
- **Backend**: Flask + SQLAlchemy + JWT
- **Frontend**: React + Styled Components
- **Infrastruktura**: Docker

## Licencja

GPLv3

## Kontakt

wkowalczykdev@gmail.com
