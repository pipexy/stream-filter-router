# !/usr/bin/env python3
"""
Stream Filter Router (SFR) initialization script.
Sets up directories, configuration files, and dependencies.
"""

import os
import sys
import shutil
import subprocess
import logging
import click
from pathlib import Path
import colorlog


# Konfiguracja kolorowego loggera
def setup_logger():
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s [SFR] %(levelname)s: %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))

    logger = colorlog.getLogger('SFR')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


logger = setup_logger()

# Struktura katalogów
DEFAULT_DIRS = {
    'config': 'config',
    'logs': 'logs',
    'recordings': 'recordings',
    'events': 'events',
    'archive': 'archive',
}

# Domyślne pliki konfiguracyjne
DEFAULT_CONFIG_FILES = {
    'stream.yaml': '''# Example stream configuration
-
  - "rtsp://camera.local:554/stream"
  - "process://motion?fps=5"
  - "hls://localhost/stream.m3u8"
''',
    'process.yaml': '''# Example process configuration
-
  filter:
   - rtsp
   - process://motion
   - hls
  run:
   - shell://ffmpeg -i $1 -c:v libx264 -preset ultrafast -c:a aac -f hls -hls_time 4 -hls_list_size 5 -y $3
''',
    '.env': '''# Environment variables
SFR_CONFIG_DIR=config
SFR_LOGS_DIR=logs
SFR_RECORDINGS_DIR=recordings
SFR_EVENTS_DIR=events
SFR_ARCHIVE_DIR=archive
'''
}


def check_dependencies():
    """Sprawdź wymagane zależności systemowe."""
    dependencies = ['ffmpeg', 'python3', 'pip3']
    missing = []

    for dep in dependencies:
        if shutil.which(dep) is None:
            missing.append(dep)

    return missing


def create_directory_structure(base_path: Path):
    """Utwórz strukturę katalogów."""
    for dir_name in DEFAULT_DIRS.values():
        dir_path = base_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")


def create_config_files(config_path: Path):
    """Utwórz domyślne pliki konfiguracyjne."""
    for filename, content in DEFAULT_CONFIG_FILES.items():
        file_path = config_path / filename
        if not file_path.exists():
            with open(file_path, 'w') as f:
                f.write(content)
            logger.info(f"Created config file: {file_path}")
        else:
            logger.warning(f"Config file already exists: {file_path}")


def install_python_requirements():
    """Zainstaluj wymagane pakiety Pythona."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        logger.info("Successfully installed Python requirements")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install requirements: {e}")
        sys.exit(1)


def create_systemd_service(base_path: Path):
    """Utwórz plik usługi systemd."""
    service_content = f'''[Unit]
Description=Stream Filter Router Service
After=network.target

[Service]
Type=simple
User={os.getenv('USER')}
WorkingDirectory={base_path}
Environment=PYTHONUNBUFFERED=1
ExecStart={sys.executable} {base_path}/stream_filter_router.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
'''

    service_path = Path('/tmp/stream-filter-router.service')
    with open(service_path, 'w') as f:
        f.write(service_content)

    logger.info(f"Created systemd service file: {service_path}")
    logger.info("To install the service, run:")
    logger.info(f"sudo mv {service_path} /etc/systemd/system/")
    logger.info("sudo systemctl daemon-reload")
    logger.info("sudo systemctl enable stream-filter-router")
    logger.info("sudo systemctl start stream-filter-router")


@click.command()
@click.option('--path', '-p', type=click.Path(), default='.',
              help='Base path for installation')
@click.option('--systemd/--no-systemd', default=False,
              help='Create systemd service file')
def main(path, systemd):
    """Initialize Stream Filter Router (SFR) environment."""
    base_path = Path(path).resolve()
    logger.info(f"Initializing SFR in: {base_path}")

    # Sprawdź zależności
    missing_deps = check_dependencies()
    if missing_deps:
        logger.error(f"Missing dependencies: {', '.join(missing_deps)}")
        logger.info("Please install them using your package manager:")
        logger.info(f"sudo apt install {' '.join(missing_deps)}")
        sys.exit(1)

    # Utwórz strukturę katalogów
    create_directory_structure(base_path)

    # Utwórz pliki konfiguracyjne
    create_config_files(base_path / DEFAULT_DIRS['config'])

    # Zainstaluj wymagania Pythona
    install_python_requirements()

    # Utwórz plik usługi systemd jeśli wymagane
    if systemd:
        create_systemd_service(base_path)

    logger.info("SFR initialization completed successfully!")
    logger.info(f"Configuration files are in: {base_path / DEFAULT_DIRS['config']}")
    logger.info("To start SFR, run: python3 stream_filter_router.py")


if __name__ == "__main__":
    main()