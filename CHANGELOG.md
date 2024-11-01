# Changelog

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
