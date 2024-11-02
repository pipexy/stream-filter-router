# Changelog

## [1.3.6] - 2024-01-09

### Dodano
- Wykrywanie istniejących procesów przy starcie:
  - Sprawdzanie procesów z pliku konfiguracyjnego
  - Wyświetlanie szczegółowych informacji o procesach
  - Monitorowanie użycia CPU i pamięci
  - Śledzenie czasu startu i działania procesów

### Zmieniono
- Ulepszono zarządzanie procesami:
  - Dodano nową klasę ManagedProcess
  - Dodano narzędzia do monitorowania procesów
  - Ulepszono formatowanie informacji o procesach
  - Dodano szczegółowe logowanie stanu procesów

## [1.3.5] - 2024-01-09

### Poprawiono
- Naprawiono błąd tworzenia procesów:
  - Usunięto konflikt między preexec_fn i start_new_session
  - Uproszczono zarządzanie grupami procesów
  - Poprawiono mechanizm zamykania procesów potomnych

## [1.3.4] - 2024-01-09

### Poprawiono
- Ulepszono mechanizm zamykania aplikacji:
  - Dodano blokadę przed wielokrotnym wywołaniem stop()
  - Dodano rekursywne zabijanie drzewa procesów
  - Ulepszono izolację procesów przez start_new_session
  - Wymuszenie zakończenia aplikacji przez sys.exit(0)
  - Poprawiono obsługę sygnałów w głównej pętli
  - Dodano zabezpieczenie przed zombie-procesami

## [1.3.3] - 2024-01-09

### Dodano
- Ulepszone zarządzanie procesami i bezpieczne zamykanie:
  - Obsługa sygnałów SIGTERM i SIGINT
  - Graceful shutdown z timeoutem dla segmentów
  - Grupowanie procesów (process groups)
  - Kolejkowanie procesów
- Zabezpieczenia przed uszkodzeniem plików wideo:
  - Dokumentacja segmentacji ffmpeg
  - Przykłady konfiguracji z timestampami
  - Automatyczna rotacja plików

### Zmieniono
- Przepisano logikę zamykania aplikacji:
  - Dodano event shutdown
  - Ulepszono obsługę wątków (daemon threads)
  - Dodano timeout dla zamykania procesów
  - Poprawiono cleanup zasobów

## [1.3.2] - 2024-01-09

### Zmieniono
- Zaktualizowano dokumentację formatów konfiguracyjnych:
  - Dodano szczegółowy opis formatu flows.json
  - Dodano szczegółowy opis formatu process.json
  - Zastąpiono przykłady YAML poprawnymi przykładami JSON
  - Dodano dokumentację parametrów URL i zmiennych w komendach

## [1.3.1] - 2024-01-09

### Zmieniono
- Przepisano logikę dopasowywania URL-i:
  - Dodano normalizację łańcuchów strumieni
  - Ulepszono parsowanie URL-i process://
  - Poprawiono obsługę schematów URL
  - Dodano lepszą obsługę tablic w konfiguracji

### Poprawiono
- Naprawiono błędy w dopasowywaniu procesów do strumieni
- Ulepszono analizę ścieżek URL
- Poprawiono obsługę parametrów zapytań

## [1.3.0] - 2024-01-09

### Dodano
- Ulepszone dopasowywanie filtrów:
  - Obsługa parametrów zapytań w URL-ach process://
  - Wsparcie dla wielu wyjść w łańcuchu strumieni
  - Elastyczne dopasowywanie schematów URL

### Poprawiono
- Naprawiono błędy w dopasowywaniu procesów do strumieni
- Zaktualizowano obsługę list w łańcuchach strumieni
- Poprawiono podstawianie zmiennych w komendach

## [1.2.0] - 2024-01-09

### Dodano
- Argumenty wiersza poleceń dla plików konfiguracyjnych:
  - `--stream-config` / `-s`: Ścieżka do pliku konfiguracji strumieni
  - `--process-config` / `-p`: Ścieżka do pliku konfiguracji procesów
  - Domyślne wartości pozostają jako `config/stream.yaml` i `config/process.yaml`

## [1.1.0] - 2024-01-09

### Dodano
- Wsparcie dla debugowania w kontenerach Docker:
  - Dodano debugpy w kontenerze sfr-main
  - Skonfigurowano porty debugowania (5678, 5679)
- Dodano brakujące zależności w kontenerach:
  - psutil dla monitorowania metryk
  - debugpy dla wsparcia debugowania

### Zmieniono
- Zaktualizowano dokumentację Docker:
  - Dodano instrukcje instalacji i uruchomienia
  - Opisano konfigurację kontenerów
  - Dodano informacje o portach i wolumenach
  - Dodano instrukcje debugowania

### Uwaga
Dla instalacji Docker:
```bash
# Tryb produkcyjny
docker compose up -d

# Tryb developerski
docker compose -f docker-compose.yml -f docker-compose.override.yml up
```

## [1.0.0] - 2024-01-09

### Dodano
- Prefix "SFR" do logów dla lepszej identyfikacji w formacie `[SFR]`
- Kolorowe formatowanie logów przy użyciu `colorlog>=6.7.0`
- Szczegółowe informacje o stanie systemu podczas inicjalizacji:
  - Status tworzenia katalogów
  - Weryfikacja zależności systemowych
  - Status instalacji wymagań Python
  - Informacje o konfiguracji systemd

### Zmieniono
- Ulepszono formatowanie komunikatów logowania:
  - DEBUG: kolor cyjan
  - INFO: kolor zielony
  - WARNING: żółty
  - ERROR: czerwony
  - CRITICAL: czerwony tekst na białym tle
- Rozszerzono dokumentację klas i metod w kodzie źródłowym
- Zaktualizowano zależności projektu:
  - pyyaml>=6.0
  - python-dotenv>=0.19.0
  - ffmpeg-python>=0.2.0
  - typing-extensions>=4.0.0
  - colorlog>=6.7.0
  - click>=8.0.0

### Uwaga
Przed uruchomieniem skryptu inicjalizacyjnego należy zainstalować wymagane zależności:
```bash
pip install -r requirements.txt
