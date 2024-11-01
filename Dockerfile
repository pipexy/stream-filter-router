FROM python:3.11-slim as base

# Zainstaluj podstawowe narzędzia i ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Utwórz użytkownika aplikacji
RUN useradd -m -r -s /bin/bash sfr

# Ustaw zmienne środowiskowe
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Zainstaluj zależności Pythona
COPY requirements.txt .
RUN pip install -r requirements.txt debugpy==1.8.0

# Skopiuj kod aplikacji
COPY . .

# Zmień właściciela plików
RUN chown -R sfr:sfr /app

USER sfr

CMD ["python", "router.py"]
