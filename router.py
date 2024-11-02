"""
Stream Filter Router (SFR)
A flexible system for routing and filtering media streams between different protocols.
Supports dynamic configuration through JSON files and custom processing filters.
"""

import json
import subprocess
import os
from typing import List, Dict, Union
import logging
import threading

from get_url_parts import get_url_parts
from match_filter import match_filter
from extract_query_params import extract_query_params
from convert_file_path import convert_file_path


class StreamFilterRouter:
    """
    Main class for handling stream routing, filtering and processing.
    Supports multiple input/output protocols and processing filters.
    """

    def __init__(self, flows_config: str, process_config: str):
        # Initialize logging first
        logging.basicConfig(
            level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
            format='%(asctime)s [SFR] %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger("StreamFilterRouter")
        
        # Then load configurations
        self.flows_config = self._load_json(flows_config)
        self.process_config = self._load_json(process_config)
        self.running_processes: Dict[str, subprocess.Popen] = {}

    def _load_json(self, file_path: str) -> dict:
        """Load and parse JSON configuration file."""
        with open(file_path, 'r') as file:
            config = json.load(file)
            self.logger.debug(f"Loaded configuration from {file_path}: {config}")
            return config

    def _find_matching_process(self, steps: List[Union[str, List[str]]]) -> dict:
        """Find matching process configuration for given flow steps."""
        self.logger.debug(f"Finding matching process for steps: {steps}")
        
        # Convert steps to a normalized format for matching
        normalized_chain = []
        for item in steps:
            if isinstance(item, list):
                # For array items, take the scheme of the first item
                scheme, _ = get_url_parts(item[0])
                normalized_chain.append(scheme)
                self.logger.debug(f"Normalized array item {item} to scheme: {scheme}")
            else:
                scheme, path = get_url_parts(item)
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
            if match_filter(process['filter'], normalized_chain):
                self.logger.info(f"Found matching process: {process}")
                return process
            else:
                self.logger.debug(f"Process #{idx} filter chain does not match")
        
        self.logger.error(f"No matching process found for normalized chain: {normalized_chain}")
        return None

    def _prepare_command(self, command: str, steps: List[Union[str, List[str]]]) -> str:
        """Prepare shell command with flow steps URLs substitution."""
        if command.startswith('shell://'):
            cmd = command[7:]  # Remove shell:// prefix
            self.logger.debug(f"Preparing command: {cmd}")
            
            # First, replace steps URLs
            stream_idx = 1
            for url in steps:
                if isinstance(url, list):
                    for i, sub_url in enumerate(url):
                        sub_url = convert_file_path(sub_url)
                        cmd = cmd.replace(f'${stream_idx}[{i}]', sub_url)
                        self.logger.debug(f"Replaced ${stream_idx}[{i}] with {sub_url}")
                else:
                    url = convert_file_path(url)
                    cmd = cmd.replace(f'${stream_idx}', url)
                    self.logger.debug(f"Replaced ${stream_idx} with {url}")
                    
                    # If this is a process:// URL, also replace its parameters
                    if url.startswith('process://'):
                        params = extract_query_params(url)
                        for key, value in params.items():
                            cmd = cmd.replace(f'${key}', value)
                            self.logger.debug(f"Replaced ${key} with {value}")
                    
                    stream_idx += 1
            
            # Remove any leading slash from the command
            cmd = cmd.lstrip('/')
            
            self.logger.debug(f"Final prepared command: {cmd}")
            return cmd
        return ''

    def _process_flow(self, name: str, steps: List[Union[str, List[str]]]):
        """Process single flow according to matching configuration."""
        self.logger.info(f"Processing flow '{name}': {steps}")
        
        process_config = self._find_matching_process(steps)
        if not process_config:
            self.logger.error(f"No matching process found for flow '{name}': {steps}")
            return

        for command in process_config['run']:
            cmd = self._prepare_command(command, steps)
            if not cmd:
                self.logger.warning(f"Empty command after preparation: {command}")
                continue

            try:
                process_id = f"{name}:{','.join(str(url) for url in steps)}"
                self.logger.info(f"Starting process {process_id}")
                self.logger.debug(f"Command: {cmd}")

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,  # Use shell to handle command substitutions
                    text=True    # Handle output as text
                )

                self.running_processes[process_id] = process
                self.logger.info(f"Started process {process_id} with PID {process.pid}")

                def log_output(pipe, prefix):
                    for line in pipe:
                        self.logger.debug(f"{prefix} [{process_id}]: {line.strip()}")

                threading.Thread(target=log_output, args=(process.stdout, "stdout")).start()
                threading.Thread(target=log_output, args=(process.stderr, "stderr")).start()

            except Exception as e:
                self.logger.error(f"Error running command {cmd}: {str(e)}", exc_info=True)

    def start(self):
        """Start processing all configured flows."""
        self.logger.info("Starting Stream Filter Router...")
        self.logger.debug(f"Loaded {len(self.flows_config['flows'])} flows")
        self.logger.debug(f"Loaded {len(self.process_config)} process configurations")
        
        for flow_config in self.flows_config['flows']:
            name = flow_config['name']
            steps = flow_config['steps']
            self.logger.debug(f"Starting thread for flow '{name}': {steps}")
            threading.Thread(target=self._process_flow, args=(name, steps)).start()
        
        self.logger.info("All flows started")

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
