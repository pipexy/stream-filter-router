# Szybki start z Stream Filter Router

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt
```
JSON
```bash
python router.py -s "config/stream.json" -p "config/process.json"
```
YAML
```bash
python router.py -s "config/stream.yaml" -p "config/process.yaml"
```
## Video stream testing
```bash
ffplay rtsp://192.168.1.2:554/Preview_01_sub
```

```bash
ffmpeg -i rtsp://192.168.1.2:554/Preview_01_sub -c copy -f segment -segment_time 6 -segment_format mp4 -strftime 1 -reset_timestamps 1 "./recordings/%Y%m%d_%H.mp4" -v debug
```




## 1. Instalacja podstawowa

```bash
# Klonowanie repozytorium
git clone https://github.com/pipexy/stream-filter-router.git
cd stream-filter-router

# Utworzenie środowiska wirtualnego
python -m venv .venv
source .venv/bin/activate

# Instalacja zależności
pip install -r requirements.txt
```

## 2. Konfiguracja

### Minimalna konfiguracja YAML
1. Utwórz `config/stream.yaml`:
```yaml
-
  - "rtsp://camera.local:554/stream"
  - "hls://localhost/stream.m3u8"
```

2. Utwórz `config/process.yaml`:
```yaml
-
  filter:
   - rtsp
   - hls
  run:
   - shell://ffmpeg -i $1 -c:v libx264 -preset ultrafast -f hls -hls_time 4 -hls_list_size 5 -y $3
```

### Minimalna konfiguracja JSON
1. Utwórz `config/stream.json`:
```json
[
  [
    "rtsp://camera.local:554/stream",
    "hls://localhost/stream.m3u8"
  ]
]
```

2. Utwórz `config/process.json`:
```json
[
  {
    "filter": ["rtsp", "hls"],
    "run": ["shell://ffmpeg -i $1 -c:v libx264 -preset ultrafast -f hls -hls_time 4 -hls_list_size 5 -y $3"]
  }
]
```

## 3. Uruchomienie

### Standardowe uruchomienie
```bash
python router.py
```

### Z określonymi plikami konfiguracyjnymi
```bash
# Dla YAML
python router.py -s "config/stream.yaml" -p "config/process.yaml"

# Dla JSON
python router.py -s "config/stream.json" -p "config/process.json"
```

## 4. Docker (opcjonalnie)

```bash
# Tryb produkcyjny
docker compose up -d

# Tryb developerski
docker compose -f docker-compose.yml -f docker-compose.override.yml up
```

## 5. Weryfikacja

1. Sprawdź logi w katalogu `logs/`
2. Otwórz strumień HLS w przeglądarce: `http://localhost:8080/stream.m3u8`
3. Sprawdź metryki na `http://localhost:9090` (w trybie Docker)

## Rozwiązywanie problemów

1. Sprawdź logi w `logs/`
2. Upewnij się, że porty nie są zajęte
3. Sprawdź połączenie ze źródłem RTSP
4. Zweryfikuj instalację ffmpeg

## Następne kroki

1. Zapoznaj się z pełną dokumentacją w README.md
2. Sprawdź przykłady w katalogu `config/`
3. Skonfiguruj monitoring
4. Dostosuj parametry ffmpeg
