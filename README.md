# Stream Filter Router (SFR)

System do przetwarzania strumieni wideo z obsługą filtrów i przekierowywania między różnymi protokołami.

## Dokumentacja

- [Szybki start](START.md) - instrukcja szybkiego rozpoczęcia pracy
- [Kontrybucja](CONTRIBUTION.md) - przewodnik dla kontrybutorów
- [Testowanie](TEST.md) - dokumentacja testów i CI/CD

## Opis

"Stream Filter Router" składa się z trzech głównych komponentów:
1. "Stream" - obsługa strumieni danych (w tym przypadku wideo)
2. "Filter" - filtrowanie i przetwarzanie strumieni
3. "Router" - przekierowywanie strumieni między różnymi protokołami/celami

## Wymagania systemowe

- Python 3.x
- ffmpeg
- pip3
- Docker (opcjonalnie)
- Docker Compose (opcjonalnie)

## Instalacja

### Standardowa instalacja

1. Sklonuj repozytorium:
```bash
git clone https://github.com/pipexy/stream-filter-router.git
cd stream-filter-router
```

2. Zainstaluj wymagane zależności Python:
```bash
pip install -r requirements.txt
```

Wymagane pakiety:
- pyyaml>=6.0
- python-dotenv>=0.19.0
- ffmpeg-python>=0.2.0
- typing-extensions>=4.0.0
- colorlog>=6.7.0
- click>=8.0.0

3. Uruchom skrypt inicjalizacyjny:
```bash
python init.py
```

### Instalacja Docker

1. Sklonuj repozytorium:
```bash
git clone https://github.com/pipexy/stream-filter-router.git
cd stream-filter-router
```

2. Uruchom w trybie produkcyjnym:
```bash
docker compose up -d
```

3. Uruchom w trybie developerskim:
```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml up
```

#### Komponenty Docker

System składa się z trzech kontenerów:
- `sfr-main`: Główny serwis przetwarzający strumienie
- `sfr-hls`: Serwer NGINX do obsługi strumieni HLS (port 8080)
- `sfr-monitor`: Serwis monitorowania z metrykami Prometheus (port 9090)

#### Porty

- 8080: Serwer HLS (NGINX)
- 9090: Metryki Prometheus
- 5678: Debugger (tryb developerski)

#### Wolumeny

- `./config`: Pliki konfiguracyjne
- `./logs`: Logi systemowe
- `./recordings`: Nagrania i strumienie HLS

## Struktura katalogów

Skrypt inicjalizacyjny utworzy następującą strukturę:
- `config/` - pliki konfiguracyjne
- `logs/` - logi systemowe
- `recordings/` - nagrania
- `events/` - zdarzenia
- `archive/` - archiwum

## Konfiguracja środowiska

### Zmienne środowiskowe
Domyślne wartości znajdują się w pliku `.env`:
```
SFR_CONFIG_DIR=config
SFR_LOGS_DIR=logs
SFR_RECORDINGS_DIR=recordings
SFR_EVENTS_DIR=events
SFR_ARCHIVE_DIR=archive
```

### Konfiguracja przepływów (flows.json)
Plik `config/flows.json` definiuje przepływy strumieni wideo:
```json
{
  "flows": [
    {
      "name": "RTSP z detekcją ruchu",
      "steps": [
        "rtsp://user:pass@camera:554/stream",
        "process://motion?fps=5&threshold=0.3",
        "file:///recordings/stream1.mp4"
      ]
    },
    {
      "name": "RTSP z zapisem czasowym", 
      "steps": [
        "rtsp://user:pass@camera:554/stream",
        "file:///recordings/%Y%m%d_%H%M.mp4"
      ]
    }
  ]
}
```

Każdy przepływ zawiera:
- `name`: Nazwa opisowa przepływu
- `steps`: Lista kroków przetwarzania, gdzie każdy krok to URL w formacie:
  - `rtsp://` - źródło RTSP
  - `process://` - proces przetwarzania z parametrami
  - `file://` - zapis do pliku (wspiera strftime format)

### Konfiguracja procesów (process.json)
Plik `config/process.json` definiuje reguły przetwarzania:
```json
[
  {
    "filter": [
      "rtsp",
      "process://motion",
      "file"
    ],
    "run": [
      "shell://ffmpeg -i $1 -c copy -f segment -segment_time 6 -segment_format mp4 -strftime 1 -reset_timestamps 1 $3"
    ]
  },
  {
    "filter": [
      "rtsp",
      "file"
    ],
    "run": [
      "shell://ffmpeg -i $1 -c copy -f segment -segment_time 6 -segment_format mp4 -strftime 1 -reset_timestamps 1 $2"
    ]
  }
]
```

Każda reguła zawiera:
- `filter`: Lista wzorców URL do dopasowania
- `run`: Lista poleceń shell do wykonania, gdzie:
  - `$1, $2, $3...` - odnoszą się do kolejnych URL-i z sekcji filter
  - Polecenia są wykonywane w kolejności zdefiniowanej w liście

### Bezpieczne zamykanie aplikacji

Aby bezpiecznie zamknąć aplikację podczas przetwarzania strumieni:

1. Użyj Ctrl+C lub wyślij sygnał SIGTERM do procesu
2. Aplikacja:
   - Zatrzyma przyjmowanie nowych strumieni
   - Poczeka na zakończenie aktualnych segmentów wideo (max 6 sekund)
   - Wyśle sygnał SIGTERM do procesów ffmpeg
   - Zamknie wszystkie uchwyty plików
   - Zakończy działanie z kodem 0

### Zapobieganie uszkodzeniom plików wideo

Aby zapobiec uszkodzeniu plików wideo przy nagłym zamknięciu:

1. Używaj segmentacji w konfiguracji ffmpeg:
```json
{
  "filter": ["rtsp", "file"],
  "run": [
    "shell://ffmpeg -i $1 -c copy -f segment -segment_time 6 -segment_format mp4 -strftime 1 -reset_timestamps 1 $2"
  ]
}
```

Kluczowe parametry:
- `-f segment`: Włącza segmentację pliku
- `-segment_time 6`: Długość segmentu w sekundach
- `-segment_format mp4`: Format segmentu
- `-strftime 1`: Umożliwia użycie znaczników czasu w nazwach
- `-reset_timestamps 1`: Reset timestampów dla każdego segmentu

2. Używaj wzorców nazw plików z datą/czasem:
```json
{
  "flows": [{
    "name": "Bezpieczny zapis RTSP",
    "steps": [
      "rtsp://kamera:554/stream",
      "file:///recordings/%Y%m%d_%H%M%S.mp4"
    ]
  }]
}
```

Zalety tego podejścia:
- Każdy segment jest osobnym, kompletnym plikiem
- Nagłe zamknięcie uszkodzi maksymalnie ostatnie 6 sekund
- Automatyczna rotacja plików
- Łatwe zarządzanie archiwum

## Uruchomienie

### Standardowe uruchomienie
```bash
python stream_filter_router.py
```

### Docker Compose
```bash
# Tryb produkcyjny
docker compose up -d

# Tryb developerski
docker compose -f docker-compose.yml -f docker-compose.override.yml up
```

Program:
- Przetwarza strumień RTSP do HLS z częstotliwością 5 FPS
- Generuje feed RSS z klatkami o częstotliwości 1 FPS
- Loguje wszystkie operacje i błędy
- Można go bezpiecznie zatrzymać używając Ctrl+C

## Instalacja jako usługa systemd

Aby zainstalować SFR jako usługę systemową:

1. Uruchom skrypt inicjalizacyjny z opcją systemd:
```bash
python init.py --systemd
```

2. Zainstaluj usługę:
```bash
sudo mv /tmp/stream-filter-router.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable stream-filter-router
sudo systemctl start stream-filter-router
```

## Monitorowanie

### Metryki Prometheus

Dostępne na porcie 9090 w trybie Docker. Metryki zawierają:
- Wykorzystanie zasobów systemowych
- Statystyki strumieni
- Status procesów

### Logi

System używa kolorowego formatowania logów:
- DEBUG: cyjan
- INFO: zielony
- WARNING: żółty
- ERROR: czerwony
- CRITICAL: czerwony tekst na białym tle

Wszystkie logi zawierają prefix "[SFR]" dla łatwej identyfikacji.

## Rozwój

### Debugowanie w trybie Docker

1. Uruchom w trybie developerskim:
```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml up
```

2. Dostępne porty debugowania:
- 5678: sfr-main
- 5679: sfr-monitor

3. Podłącz debugger (np. VS Code) do odpowiedniego portu
