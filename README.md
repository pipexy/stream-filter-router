# Stream Filter Router (SFR)

System do przetwarzania strumieni wideo z obsługą filtrów i przekierowywania między różnymi protokołami.

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

### Konfiguracja strumieni
Plik `config/stream.yaml`:
```yaml
# Przykład konfiguracji strumienia
-
  - "rtsp://camera.local:554/stream"
  - "process://motion?fps=5"
  - "hls://localhost/stream.m3u8"
```

### Konfiguracja procesów
Plik `config/process.yaml`:
```yaml
# Przykład konfiguracji procesu
-
  filter:
   - rtsp
   - process://motion
   - hls
  run:
   - shell://ffmpeg -i $1 -c:v libx264 -preset ultrafast -c:a aac -f hls -hls_time 4 -hls_list_size 5 -y $3
```

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



## START
```bash
# Utwórz venv
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# Zainstaluj zależności
pip install -r requirements.txt -r requirements-dev.txt
```


```bash
python router.py
```

```bash
python router.py -s "config/stream.yaml" -p "config/process.yaml"
```

```bash
python router.py -s ".config/stream.yaml" -p ".config/process.yaml"
```
