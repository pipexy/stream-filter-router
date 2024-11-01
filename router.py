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
        # Initialize logging first
        logging.basicConfig(
            level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
            format='%(asctime)s [SFR] %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger("StreamFilterRouter")
        
        # Then load configurations
        self.stream_config = self._load_yaml(stream_config)
        self.process_config = self._load_yaml(process_config)
        self.running_processes: Dict[str, subprocess.Popen] = {}

    def _load_yaml(self, file_path: str) -> dict:
        """Load and parse YAML configuration file."""
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
            self.logger.debug(f"Loaded configuration from {file_path}: {config}")
            return config

    def _get_url_parts(self, url: str) -> tuple:
        """Get scheme and base path from URL without query parameters."""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        self.logger.debug(f"Parsing URL {url} -> scheme: {parsed.scheme}, path: {path}")
        return parsed.scheme, path

    def _find_matching_process(self, stream_chain: List[Union[str, List[str]]]) -> dict:
        """Find matching process configuration for given stream chain."""
        self.logger.debug(f"Finding matching process for stream chain: {stream_chain}")
        
        # Convert stream chain to a normalized format for matching
        normalized_chain = []
        for item in stream_chain:
            if isinstance(item, list):
                # For array items, take the scheme of the first item
                scheme, _ = self._get_url_parts(item[0])
                normalized_chain.append(scheme)
                self.logger.debug(f"Normalized array item {item} to scheme: {scheme}")
            else:
                scheme, path = self._get_url_parts(item)
                if scheme == 'process':
                    # For process URLs, include the base path
                    normalized_chain.append(f"{scheme}://{path}")
                    self.logger.debug(f"Normalized process URL {item} to: {scheme}://{path}")
                else:
                    # For other URLs, just the scheme
                    normalized_chain.append(scheme)
                    self.logger.debug(f"Normalized URL {item} to scheme: {scheme}")

        self.logger.info(f"Normalized chain for matching: {normalized_chain}")

        # Try to find a matching process
        for idx, process in enumerate(self.process_config):
            self.logger.debug(f"Checking process config #{idx}: {process}")
            if self._match_filter(process['filter'], normalized_chain):
                self.logger.info(f"Found matching process: {process}")
                return process
            else:
                self.logger.debug(f"Process #{idx} filter chain does not match")
        
        self.logger.error(f"No matching process found for normalized chain: {normalized_chain}")
        return None

    def _match_filter(self, filter_chain: List[str], normalized_chain: List[str]) -> bool:
        """Match normalized chain against filter chain."""
        self.logger.debug(f"Matching filter chain {filter_chain} against normalized chain {normalized_chain}")
        
        if len(filter_chain) != len(normalized_chain):
            self.logger.debug(f"Length mismatch: filter chain ({len(filter_chain)}) != normalized chain ({len(normalized_chain)})")
            return False

        for idx, (filter_url, norm_url) in enumerate(zip(filter_chain, normalized_chain)):
            self.logger.debug(f"Comparing position {idx}: filter '{filter_url}' vs normalized '{norm_url}'")
            
            filter_scheme, filter_path = self._get_url_parts(filter_url)
            
            if '://' in norm_url:
                # This is a process:// URL
                norm_scheme, norm_path = self._get_url_parts(norm_url)
                if filter_scheme != norm_scheme or filter_path != norm_path:
                    self.logger.debug(f"Process URL mismatch at position {idx}")
                    self.logger.debug(f"Filter: scheme={filter_scheme}, path={filter_path}")
                    self.logger.debug(f"Norm: scheme={norm_scheme}, path={norm_path}")
                    return False
            else:
                # This is just a scheme
                if filter_scheme != norm_url:
                    self.logger.debug(f"Scheme mismatch at position {idx}: {filter_scheme} != {norm_url}")
                    return False

        self.logger.debug("Filter chain matches normalized chain")
        return True

    def _prepare_command(self, command: str, stream_chain: List[Union[str, List[str]]]) -> List[str]:
        """Prepare shell command with stream URLs substitution."""
        if command.startswith('shell://'):
            cmd = command[7:]
            self.logger.debug(f"Preparing command: {cmd}")
            stream_idx = 1
            for url in stream_chain:
                if isinstance(url, list):
                    for i, sub_url in enumerate(url):
                        cmd = cmd.replace(f'${stream_idx}[{i}]', sub_url)
                        self.logger.debug(f"Replaced ${stream_idx}[{i}] with {sub_url}")
                else:
                    cmd = cmd.replace(f'${stream_idx}', url)
                    self.logger.debug(f"Replaced ${stream_idx} with {url}")
                    stream_idx += 1
            
            self.logger.debug(f"Final prepared command: {cmd}")
            return cmd.split()
        return []

    def _process_stream(self, stream_chain: List[Union[str, List[str]]]):
        """Process single stream chain according to matching configuration."""
        self.logger.info(f"Processing stream chain: {stream_chain}")
        
        process_config = self._find_matching_process(stream_chain)
        if not process_config:
            self.logger.error(f"No matching process found for stream chain: {stream_chain}")
            return

        for command in process_config['run']:
            cmd = self._prepare_command(command, stream_chain)
            if not cmd:
                self.logger.warning(f"Empty command after preparation: {command}")
                continue

            try:
                process_id = f"{','.join(str(url) for url in stream_chain)}"
                self.logger.info(f"Starting process {process_id}")
                self.logger.debug(f"Command: {' '.join(cmd)}")

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                self.running_processes[process_id] = process
                self.logger.info(f"Started process {process_id} with PID {process.pid}")

                def log_output(pipe, prefix):
                    for line in pipe:
                        self.logger.debug(f"{prefix} [{process_id}]: {line.decode().strip()}")

                threading.Thread(target=log_output, args=(process.stdout, "stdout")).start()
                threading.Thread(target=log_output, args=(process.stderr, "stderr")).start()

            except Exception as e:
                self.logger.error(f"Error running command {cmd}: {str(e)}", exc_info=True)

    def start(self):
        """Start processing all configured stream chains."""
        self.logger.info("Starting Stream Filter Router...")
        self.logger.debug(f"Loaded {len(self.stream_config)} stream chains")
        self.logger.debug(f"Loaded {len(self.process_config)} process configurations")
        
        for stream_chain in self.stream_config:
            self.logger.debug(f"Starting thread for stream chain: {stream_chain}")
            threading.Thread(target=self._process_stream, args=(stream_chain,)).start()
        
        self.logger.info("All stream chains started")

    def stop(self):
        """Stop all running processes and clean up."""
        self.logger.info("Stopping Stream Filter Router...")
        for process_id, process in self.running_processes.items():
            try:
                self.logger.debug(f"Terminating process {process_id} with PID {process.pid}")
                process.terminate()
                self.logger.info(f"Terminated process: {process_id}")
            except Exception as e:
                self.logger.error(f"Error terminating process {process_id}: {str(e)}", exc_info=True)
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
