# Testowanie Stream Filter Router

## Testy jednostkowe

### Uruchomienie testów
```bash
# Instalacja zależności deweloperskich
pip install -r requirements-dev.txt

# Uruchomienie wszystkich testów
pytest

# Uruchomienie testów z pokryciem kodu
pytest --cov=.

# Uruchomienie konkretnego testu
pytest tests/test_router.py
```

## Struktura testów

```
tests/
├── test_router.py
├── test_match_filter.py
├── test_get_url_parts.py
├── test_extract_query_params.py
└── test_convert_file_path.py
```

## Przypadki testowe

### Router
- Poprawne przekierowanie strumienia
- Obsługa błędów połączenia
- Walidacja konfiguracji

### Filtry
- Dopasowanie wzorców URL
- Przetwarzanie parametrów
- Obsługa różnych protokołów

### Parsowanie URL
- Poprawne części URL
- Obsługa specjalnych znaków
- Walidacja protokołów

## Testy integracyjne

### Przygotowanie środowiska
```bash
# Uruchomienie kontenerów testowych
docker compose -f docker-compose.test.yml up -d

# Sprawdzenie statusu
docker compose ps
```

### Scenariusze testowe
1. Pełny przepływ RTSP -> HLS
2. Monitoring i metryki
3. Obsługa wielu strumieni
4. Restart i odzyskiwanie

## Testy wydajnościowe

### Metryki
- Wykorzystanie CPU
- Wykorzystanie pamięci
- Opóźnienie strumienia
- Przepustowość sieci

### Narzędzia
```bash
# Monitoring zasobów
docker stats

# Testy obciążeniowe
ab -n 1000 -c 10 http://localhost:8080/stream.m3u8
```

## Testy bezpieczeństwa

### Obszary testów
1. Walidacja wejścia
2. Uprawnienia dostępu
3. Bezpieczeństwo sieci
4. Obsługa błędów

### Narzędzia
- OWASP ZAP
- Nmap
- Wireshark

## Testy end-to-end

### Scenariusze
1. Konfiguracja -> uruchomienie -> streaming -> monitoring
2. Obsługa awarii -> restart -> odzyskiwanie
3. Skalowanie -> wiele strumieni -> wydajność

### Weryfikacja
- Jakość strumienia
- Stabilność systemu
- Poprawność metryk
- Logi systemowe

## Continuous Integration

### GitHub Actions
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest
```

## Raportowanie błędów

### Format zgłoszenia
```
Tytuł: [Komponent] Krótki opis problemu

Środowisko:
- OS: Ubuntu 20.04
- Python: 3.8
- Docker: 20.10

Kroki do reprodukcji:
1. ...
2. ...
3. ...

Oczekiwane zachowanie:
...

Aktualne zachowanie:
...

Logi:
...
