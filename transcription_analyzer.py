from huggingface_hub import InferenceClient
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


class TranscriptionAnalyzer:
    """System analizy transkrypcji dla różnych typów spotkań"""

    def __init__(self, api_key):
        self.client = InferenceClient(
            provider="novita",
            api_key=api_key
        )
        self.model = "deepseek-ai/DeepSeek-R1"

    def load_transcription(self, filepath):
        """Wczytuje transkrypcję z pliku"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ Błąd: Nie znaleziono pliku {filepath}")
            return None

    def save_output(self, content, output_name):
        """Zapisuje wynik do pliku"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_name}_{timestamp}.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Zapisano: {filename}")
        return filename

    def analyze(self, transcription, prompt_type="universal"):
        """Główna metoda analizy"""

        prompts = {
            "universal": self._prompt_universal(transcription),
            "organizational": self._prompt_organizational(transcription),
            "lecture": self._prompt_lecture(transcription),
            "panel": self._prompt_panel(transcription),
            "difficult": self._prompt_difficult(transcription),
            "wrss": self._prompt_wrss(transcription)

        }

        if prompt_type not in prompts:
            print(f"⚠️ Nieznany typ: {prompt_type}. Używam 'universal'")
            prompt_type = "universal"

        print(f"🔄 Analizuję transkrypcję ({prompt_type})...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompts[prompt_type]}
                ],
                max_tokens=4000
            )

            result = response.choices[0].message.content
            print("✅ Analiza zakończona")
            return result

        except Exception as e:
            print(f"❌ Błąd podczas analizy: {e}")
            return None

    def _prompt_universal(self, transcription):
        return f"""Jesteś ekspertem w analizie rozmów i tworzeniu profesjonalnych notatek. Na podstawie poniższej transkrypcji stwórz szczegółowy, uporządkowany konspekt.

TRANSKRYPCJA:
{transcription}

INSTRUKCJE:
1. **Rozpoznaj typ spotkania** (debata, wykład, dyskusja, warsztaty)
2. **Zidentyfikuj uczestników** i ich role
3. **Wyodrębnij strukturę** (agenda, tematy główne, wątki poboczne)
4. **Zachwyć styl wypowiedzi**: 
   - Czy mówcy są formalni czy swobodni?
   - Czy używają żargonu technicznego?
   - Jaki jest ton rozmowy?
5. **Stwórz konspekt zawierający**:
   - Metadane (typ spotkania, data, uczestnicy)
   - Kluczowe tematy z timestampami
   - Najważniejsze cytaty z kontekstem
   - Decyzje/wnioski/action items
   - Pytania bez odpowiedzi

FORMAT WYJŚCIOWY:
- Używaj nagłówków markdown (##, ###)
- Cytaty w blokach > 
- Listy numerowane dla kroków/decyzji
- Listy punktowane dla szczegółów
- Wyróżnij **kluczowe terminy**

Konspekt powinien być profesjonalny, zwięzły i łatwy do przeglądania."""

    def _prompt_organizational(self, transcription):
        return f"""Jesteś asystentem zarządzającym dokumentacją zebrań. Przeanalizuj poniższą transkrypcję spotkania samorządowego i stwórz protokół.

TRANSKRYPCJA:
{transcription}

ZADANIA:
1. **Identyfikacja mówców**:
   - Przypisz każdemu mówcy rolę (przewodniczący, kandydat, moderator)
   - Oznacz zmienne jakości rozpoznania głosu

2. **Struktura protokołu**:
   ## PROTOKÓŁ ZE SPOTKANIA
   **Data**: [wyciągnij z kontekstu]
   **Uczestnicy**: [lista z rolami]
   **Agenda**: [punkty programu]

   ### PRZEBIEG SPOTKANIA
   [chronologiczny opis z timestampami]

   ### KLUCZOWE WYPOWIEDZI
   [cytaty z przypisaniem do mówców]

   ### DECYZJE I USTALENIA
   - [ ] Action item 1
   - [ ] Action item 2

   ### PYTANIA DO ROZSTRZYGNIĘCIA
   [lista otwartych kwestii]

3. **Weryfikacja spójności**:
   - Czy wszystkie wypowiedzi są przypisane do właściwych osób?
   - Czy jest ciągłość tematyczna?
   - Czy brakuje fragmentów rozmowy?

UWAGA: Zachowaj formalny ton dokumentu urzędowego."""

    def _prompt_lecture(self, transcription):
        return f"""Jesteś asystentem dydaktycznym tworzącym notatki z wykładu. Przeanalizuj poniższą transkrypcję i stwórz materiał do nauki.

TRANSKRYPCJA:
{transcription}

STRUKTURA NOTATKI:

## 📚 NOTATKI Z WYKŁADU

### INFORMACJE PODSTAWOWE
- **Temat**: [tytuł wykładu]
- **Prowadzący**: [imię i nazwisko]
- **Czas trwania**: [oblicz z timestampów]
- **Poziom**: [początkujący/średniozaawansowany/zaawansowany]

### SŁOWA KLUCZOWE
[lista 10-15 najważniejszych terminów]

### PLAN WYKŁADU
1. [temat 1] - [timestamp]
2. [temat 2] - [timestamp]

### SZCZEGÓŁOWE OMÓWIENIE

#### [Temat 1]
**Definicja**: [zwięzłe wyjaśnienie]

**Kluczowe koncepcje**:
- Punkt 1
- Punkt 2

**Przykłady**: 
> [cytaty z wykładu ilustrujące temat]

**Wzory/Schematy**:
```
[jeśli są wzory matematyczne lub kody]
```

### PODSUMOWANIE
[3-5 najważniejszych wniosków]

### PYTANIA DO DALSZEJ ANALIZY
[pytania, które wykładowca pozostawił otwarte]

### MATERIAŁY DODATKOWE
[wspomniane źródła, książki, linki]

WYTYCZNE:
- Używaj **pogrubienia** dla definicji
- Używaj `kodu` dla terminów technicznych
- Twórz diagramy tekstowe tam gdzie to możliwe
- Zaznacz fragmenty "⚠️ WAŻNE" dla kluczowych informacji"""

    def _prompt_panel(self, transcription):
        return f"""Jesteś moderatorem dyskusji tworzącym raport z panelu ekspertów. Przeanalizuj chaotyczną dyskusję i uporządkuj ją.

TRANSKRYPCJA:
{transcription}

WYZWANIA DO ROZWIĄZANIA:
- Nakładające się wypowiedzi
- Przerwania i wtrącenia
- Nieukończone zdania
- Brak wyraźnych zmian mówców

INSTRUKCJE:

1. **MAPA UCZESTNIKÓW**
| Mówca | Rola/Ekspertyza | Częstotliwość wypowiedzi |
|-------|----------------|-------------------------|
| A     | [opis]         | [%]                     |

2. **REKONSTRUKCJA WĄTKÓW**
Dla każdego tematu:

### 🔹 TEMAT: [nazwa]
**Czas**: [XX:XX - YY:YY]

**Stanowiska**:
- **Mówca A**: [streszczenie opinii]
  > "Kluczowy cytat"

- **Mówca B**: [kontropinia]
  > "Odpowiedź na poprzednika"

**Punkty sporne**:
- [Różnica 1]
- [Różnica 2]

**Konsensus**:
- [Wspólne ustalenia]

3. **DYNAMIKA DYSKUSJI**
- Kto dominował? [analiza]
- Czy były momenty napięcia? [timestamp + opis]
- Nieudzielone odpowiedzi na pytania

4. **SYNTEZA**
GŁÓWNE WNIOSKI:
✅ Uzgodnione
❓ Do dalszej dyskusji
❌ Odrzucone pomysły

UWAGA: Jeśli fragment jest niezrozumiały, oznacz [NIEJASNE: XX:XX] i kontynuuj."""

    def _prompt_difficult(self, transcription):
        return f"""Jesteś ekspertem w rekonstrukcji uszkodzonych transkrypcji. Masz do czynienia z nagraniem niskiej jakości.

TRANSKRYPCJA (Z BŁĘDAMI):
{transcription}

ZNANE PROBLEMY:
- Szumy tła i echo
- Pomyłki w rozpoznawaniu słów
- Brakujące fragmenty
- Mylne przypisanie mówców

ZADANIE - ANALIZA FORENSYCZNA:

## 1️⃣ DIAGNOZA JAKOŚCI
**Ogólna ocena**: [1-10]
**Problematyczne fragmenty**:
- [XX:XX - YY:YY]: [opis problemu]

## 2️⃣ REKONSTRUKCJA TEKSTU

Dla każdego fragmentu:
[ORYGINALNY ZAPIS]
"[tekst z błędami]"

[PRAWDOPODOBNA INTERPRETACJA]
"[poprawiona wersja]"

[POZIOM PEWNOŚCI]: ⭐⭐⭐⭐☆ (4/5)

## 3️⃣ WERYFIKACJA MÓWCÓW
| Timestamp | Przypisany | Prawdopodobny | Pewność |
|-----------|-----------|---------------|---------|
| 00:15     | Mówca A   | Mówca B (?)   | 60%     |

## 4️⃣ WYPEŁNIANIE LUK

Dla brakujących fragmentów:
[XX:XX] [LUKA - 15 sekund]
Kontekst przed: "..."
Kontekst po: "..."
Prawdopodobna treść: [hipoteza oparta na kontekście]

## 5️⃣ KONSPEKT Z ZASTRZEŻENIAMI

[Standardowy konspekt z oznaczeniami:]
- ✅ Fragmenty pewne
- ⚠️ Fragmenty zrekonstruowane
- ❌ Fragmenty niemożliwe do odtworzenia

## 6️⃣ REKOMENDACJE
- Które fragmenty wymagają ponownego nagrania?
- Jakie usprawnienia techniczne zaproponować?
- Alternatywne źródła informacji (notatki uczestników, slajdy)?

FILOZOFIA: Lepiej oznaczyć niepewność niż wymyślać treść."""


    def _prompt_wrss(self, transcription):
        return f"""Jesteś asystentem analizującym transkrypcje ze spotkań Wydziałowej Rady Samorządu Studenckiego (WRSS). 
Transkrypcja może zawierać błędy rozpoznawania mowy, przekręcone słowa, brakujące fragmenty lub błędne przypisanie mówców.

TRANSKRYPCJA:
{transcription}

TWOJE ZADANIA:

## 1. WSTĘPNE ROZPOZNANIE
- Jaki był charakter spotkania? (głosowanie, dyskusja, informacyjne, awaryjne)
- Czy transkrypcja jest kompletna? Oceń poziom jakości (1–10) i wskaż najbardziej zniszczone fragmenty.

## 2. UCZESTNICY I ROLA
- Spróbuj rozpoznać mówców (jeśli imię/nazwisko niejasne → oznacz jako „Nieznany 1”, „Nieznany 2”).
- Jeżeli można wywnioskować rolę (przewodniczący, viceprzewodnicząca, koordynator wydarzenia - zapisz nazwe wydarzenia) – zapisz.

## 3. STRUKTURA SPOTKANIA (PROTOKÓŁ)

### 📌 PRZEBIEG (chronologicznie)
Dla każdego tematu:
- **Temat**: [nazwa lub „niezrozumiałe”]
- **Streszczenie dyskusji**
- **Cytaty** → używaj `>` + oznacz mówcę, a w razie błędów `(? niepewne)`
- najważniejsze bullet pointy - co zostało ustalone etc
- czy jest coś ważnego co nie dostało odpowiedzi - wskaż wątki które powinny zostać podniesione ponownie

### 📌 DECYZJE / GŁOSOWANIA / USTALENIA
- Zebrane w formie listy:
  - [ ] Decyzja 1 – kto, czego dotyczy, wynik
  - [ ] Decyzja 2 …

### 📌 OTWARTE TEMATY / DO USTALENIA
- Pytania bez odpowiedzi
- Zadania, którym nie przypisano osoby

## 4. OBSŁUGA BŁĘDÓW TRANSKRYPCJI
- Jeśli zdanie jest ewidentnie błędne, spróbuj poprawić i wywnioskować cel:
  „studnia akademicka” → („studenci akademiccy”?)
- Jeśli brak kontekstu → zostaw jako `[?]` bez wymyślania.
- Jeśli ktoś przerywa komuś – napisz „[nakładanie wypowiedzi]” - w przypadkach kiedy watek jest znaczny.

## 5. FORMAT
- Markdown, nagłówki (##, ###)
- Cytaty w `>`
- Fragmenty niepewne oznaczaj ⚠️
- Nie dopisuj nic spoza transkrypcji – lepiej zostawić znak zapytania niż zgadywać.

Pamiętaj: celem jest możliwie rzetelne odtworzenie przebiegu WRSS mimo słabej jakości materiału."""



# ============================================================
# PRZYKŁADY UŻYCIA
# ============================================================

def main():
    """Przykłady użycia systemu"""

    # Inicjalizacja
    API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    analyzer = TranscriptionAnalyzer(API_KEY)

    print("=" * 60)
    print("  SYSTEM ANALIZY TRANSKRYPCJI")
    print("=" * 60)

    # Menu wyboru
    print("\nDostępne tryby analizy:")
    print("1. Universal - uniwersalny (domyślny)")
    print("2. Organizational - spotkania organizacyjne")
    print("3. Lecture - wykłady i webinary")
    print("4. Panel - dyskusje panelowe")
    print("5. Difficult - trudne warunki (szumy, błędy)")

    choice = input("\nWybierz tryb (1-5) lub Enter dla domyślnego: ").strip()

    mode_map = {
        "1": "universal",
        "2": "organizational",
        "3": "lecture",
        "4": "panel",
        "5": "difficult",
        "6": "wrss",
        "": "universal"
    }

    mode = mode_map.get(choice, "universal")

    # Wczytanie pliku
    filename = input("\nPodaj nazwę pliku (domyślnie: transkrypcja.txt): ").strip()
    if not filename:
        filename = "transcripts/transkrypcja_timeline.txt"

    transcription = analyzer.load_transcription(filename)

    if transcription:
        # Analiza
        result = analyzer.analyze(transcription, prompt_type=mode)

        if result:
            # Wyświetlenie
            print("\n" + "=" * 60)
            print("WYNIK ANALIZY:")
            print("=" * 60)
            print(result)

            # Zapis
            save = input("\n💾 Zapisać do pliku? (t/n): ").strip().lower()
            if save == 't':
                output_name = f"konspekt_{mode}"
                analyzer.save_output(result, output_name)

    print("\n✅ Zakończono")


if __name__ == "__main__":
    main()