Dodajmy debugpy do zależności i zaktualizujmy konfigurację dla developmentu.


Aby uruchomić z debugowaniem:

1. Najpierw stwórz wszystkie pliki z konfiguracji powyżej.

2. Uruchom w trybie debug:
```bash
docker compose -f docker-compose.yml -f docker-compose.debug.yml up --build
```

3. Konfiguracja VS Code:
- Zainstaluj rozszerzenie Python
- Ustaw punkt wstrzymania (breakpoint) w kodzie
- Użyj konfiguracji "SFR: Remote Debug" z panelu Debug

4. Struktura projektu po aktualizacji:
```
stream-filter-router/
├── Dockerfile
├── Dockerfile.dev
├── docker-compose.yml
├── docker-compose.debug.yml
├── requirements.txt
├── requirements-dev.txt
├── .vscode/
│   └── launch.json
└── ...
```


Utwórz venv
```bash
python -m venv .venv
source .venv/bin/activate
```

Zainstaluj zależności
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Główne zmiany:
1. Dodano osobny `requirements-dev.txt` z zależnościami deweloperskimi
2. Utworzono osobny `Dockerfile.dev` z konfiguracją dla developmentu
3. Dodano `docker-compose.debug.yml` z konfiguracją debugowania
4. Dodano konfigurację VS Code dla zdalnego debugowania

Teraz możesz:
- Używać debuggera w VS Code
- Ustawiać breakpointy
- Sprawdzać zmienne
- Wykonywać kod krok po kroku
- Hot-reloadować zmiany w kodzie

Aby sprawdzić czy debugger działa:
1. Dodaj breakpoint w kodzie
2. Uruchom debugowanie w VS Code
3. Wykonaj akcję która uruchomi kod z breakpointem
4. VS Code powinien zatrzymać się na breakpoincie

Czy potrzebujesz dodatkowych wyjaśnień odnośnie debugowania lub konfiguracji?