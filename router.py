"""
Stream Filter Router (SFR)
A flexible system for routing and filtering media streams between different protocols.
Supports dynamic configuration through YAML files and custom processing filters.
"""

import yaml
import subprocess
import os
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Union
import logging
import threading
import time
import click


class StreamFilterRouter:
    """
    Main class for handling stream routing, filtering and processing.
    Supports multiple input/output protocols and processing filters.
    """

    def __init__(self, stream_config: str, process_config: str):
        self.stream_config = self._load_yaml(stream_config)
        self.process_config = self._load_yaml(process_config)
        self.running_processes: Dict[str, subprocess.Popen] = {}
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [SFR] %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger("StreamFilterRouter")

    def _load_yaml(self, file_path: str) -> dict:
        """Load and parse YAML configuration file."""
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def _parse_url(self, url: str) -> tuple:
        """Parse URL into scheme, path and query parameters."""
        parsed = urlparse(url)
        scheme = parsed.scheme
        path = parsed.path
        query = parse_qs(parsed.query)
        return scheme, path, query

    def _find_matching_process(self, stream_chain: List[Union[str, List[str]]]) -> dict:
        """Find matching process configuration for given stream chain."""
        for process in self.process_config:
            if self._match_filter(process['filter'], stream_chain):
                return process
        return None

    def _match_filter(self, filter_chain: List[str], stream_chain: List[Union[str, List[str]]]) -> bool:
        """Match stream chain against filter chain configuration."""
        if len(filter_chain) != len([s for s in stream_chain if isinstance(s, str)]):
            return False

        filter_idx = 0
        for stream_url in stream_chain:
            if isinstance(stream_url, list):
                continue
            
            filter_url = filter_chain[filter_idx]
            filter_scheme = urlparse(filter_url).scheme
            stream_scheme = urlparse(stream_url).scheme
            
            # Handle process:// URLs with query parameters
            if filter_scheme == 'process' and stream_scheme == 'process':
                filter_path = urlparse(filter_url).path.strip('/')
                stream_path = urlparse(stream_url).path.strip('/')
                if filter_path != stream_path:
                    return False
            # For other URLs, just match the scheme
            elif filter_scheme != stream_scheme:
                return False
            
            filter_idx += 1
            
        return True

    def _prepare_command(self, command: str, stream_chain: List[Union[str, List[str]]]) -> List[str]:
        """Prepare shell command with stream URLs substitution."""
        if command.startswith('shell://'):
            cmd = command[7:]
            stream_idx = 1
            for url in stream_chain:
                if isinstance(url, list):
                    for i, sub_url in enumerate(url):
                        cmd = cmd.replace(f'${stream_idx}[{i}]', sub_url)
                else:
                    cmd = cmd.replace(f'${stream_idx}', url)
                    stream_idx += 1
            return cmd.split()
        return []

    def _process_stream(self, stream_chain: List[Union[str, List[str]]]):
        """Process single stream chain according to matching configuration."""
        process_config = self._find_matching_process(stream_chain)
        if not process_config:
            self.logger.error(f"No matching process found for stream chain: {stream_chain}")
            return

        for command in process_config['run']:
            cmd = self._prepare_command(command, stream_chain)
            if not cmd:
                continue

            try:
                process_id = f"{','.join(str(url) for url in stream_chain)}"

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                self.running_processes[process_id] = process
                self.logger.info(f"Started process {process_id} with command: {' '.join(cmd)}")

                def log_output(pipe, prefix):
                    for line in pipe:
                        self.logger.info(f"{prefix}: {line.decode().strip()}")

                threading.Thread(target=log_output, args=(process.stdout, "stdout")).start()
                threading.Thread(target=log_output, args=(process.stderr, "stderr")).start()

            except Exception as e:
                self.logger.error(f"Error running command {cmd}: {str(e)}")

    def start(self):
        """Start processing all configured stream chains."""
        self.logger.info("Starting Stream Filter Router...")
        for stream_chain in self.stream_config:
            threading.Thread(target=self._process_stream, args=(stream_chain,)).start()
        self.logger.info("All stream chains started")

    def stop(self):
        """Stop all running processes and clean up."""
        self.logger.info("Stopping Stream Filter Router...")
        for process_id, process in self.running_processes.items():
            try:
                process.terminate()
                self.logger.info(f"Terminated process: {process_id}")
            except Exception as e:
                self.logger.error(f"Error terminating process {process_id}: {str(e)}")
        self.running_processes.clear()
        self.logger.info("Stream Filter Router stopped")


@click.command()
@click.option('--stream-config', '-s', 
              default="config/stream.yaml",
              help="Path to stream configuration YAML file",
              type=click.Path(exists=True))
@click.option('--process-config', '-p',
              default="config/process.yaml",
              help="Path to process configuration YAML file",
              type=click.Path(exists=True))
def main(stream_config: str, process_config: str):
    """Main entry point for the Stream Filter Router."""
    router = StreamFilterRouter(stream_config, process_config)

    try:
        router.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        router.stop()
        logging.info("Stream Filter Router shutdown complete")


if __name__ == "__main__":
    main()
