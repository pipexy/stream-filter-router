# stream-filter-router
SFR


"Stream Filter Router"

1. "Stream" - obsługa strumieni danych (w tym przypadku wideo)
2. "Filter" - filtrowanie i przetwarzanie strumieni
3. "Router" - przekierowywanie strumieni między różnymi protokołami/celami


- StreamPipeRouter (SPR) - podkreśla aspekt "pipeline'owania" danych
- MediaStreamOrchestrator (MSO) - akcentuje zarządzanie wieloma strumieniami
- StreamFilterPipeline (SFP) - skupia się na przetwarzaniu potokowym
- MediaFlowDirector (MFD) - podkreśla kierowanie przepływem mediów




Pomogę Ci stworzyć system przetwarzania strumieni z RTSP do HLS z obsługą filtrów. Stworzę kompletne rozwiązanie w Pythonie.




1. Wczytywanie konfiguracji ze plików YAML
2. Dopasowywanie strumieni do odpowiednich procesów na podstawie filtrów
3. Uruchamianie poleceń shell z podstawianiem odpowiednich URL-i
4. Obsługa wielu strumieni jednocześnie w osobnych wątkach
5. Logowanie outputu procesów
6. Bezpieczne zamykanie procesów

Aby użyć tego kodu:

1. Zapisz go jako `stream_processor.py`
2. Umieść pliki `stream.yaml` i `process.yaml` w tym samym katalogu
3. Uruchom program:
```bash
python stream_processor.py
```

Program będzie:
- Przetwarzał strumień RTSP do HLS z częstotliwością 5 FPS
- Generował feed RSS z klatkami o częstotliwości 1 FPS
- Logował wszystkie operacje i błędy
- Można go bezpiecznie zatrzymać używając Ctrl+C

Czy chciałbyś, żebym wyjaśnił jakąś konkretną część implementacji lub dodał dodatkowe funkcjonalności?



# stream.yaml - przykłady konfiguracji strumieni
---
---
# process.yaml - przykłady konfiguracji procesów
---
