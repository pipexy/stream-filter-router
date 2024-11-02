"""
Stream Filter Router (SFR)
A flexible system for routing and filtering media streams between different protocols.
Supports dynamic configuration through JSON files and custom processing filters.
"""

import json
import os
import signal
import time
import sys
from typing import List, Dict, Union
import logging
import threading
from queue import Queue

from get_url_parts import get_url_parts
from match_filter import match_filter
from extract_query_params import extract_query_params
from convert_file_path import convert_file_path
from process import ManagedProcess, ProcessState
from process_utils import check_existing_processes


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
        self.process_config_path = process_config
        self.process_config = self._load_json(process_config)
        self.running_processes: Dict[str, ManagedProcess] = {}
        self.shutdown_event = threading.Event()
        self._shutdown_lock = threading.Lock()
        self._is_shutting_down = False

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

    def _handle_process_output(self, process_id: str, line: str):
        """Handle process stdout data."""
        self.logger.debug(f"stdout [{process_id}]: {line}")

    def _handle_process_error(self, process_id: str, line: str):
        """Handle process stderr data."""
        self.logger.debug(f"stderr [{process_id}]: {line}")

    def _handle_process_exit(self, process_id: str, exit_code: int):
        """Handle process exit."""
        self.logger.info(f"Process {process_id} exited with code {exit_code}")
        if process_id in self.running_processes:
            del self.running_processes[process_id]

    def _process_flow(self, name: str, steps: List[Union[str, List[str]]]):
        """Process single flow according to matching configuration."""
        self.logger.info(f"Processing flow '{name}': {steps}")
        
        process_config = self._find_matching_process(steps)
        if not process_config:
            self.logger.error(f"No matching process found for flow '{name}': {steps}")
            return

        for command in process_config['run']:
            if self.shutdown_event.is_set():
                self.logger.info(f"Shutdown requested, skipping new process for flow '{name}'")
                return

            cmd = self._prepare_command(command, steps)
            if not cmd:
                self.logger.warning(f"Empty command after preparation: {command}")
                continue

            try:
                process_id = f"{name}:{','.join(str(url) for url in steps)}"
                self.logger.info(f"Starting process {process_id}")
                self.logger.debug(f"Command: {cmd}")

                # Create managed process
                process = ManagedProcess(
                    name=process_id,
                    command=cmd,
                    on_output=lambda line: self._handle_process_output(process_id, line),
                    on_error=lambda line: self._handle_process_error(process_id, line),
                    on_exit=lambda code: self._handle_process_exit(process_id, code)
                )

                if process.start():
                    self.running_processes[process_id] = process
                    self.logger.info(f"Started process {process_id}")
                else:
                    self.logger.error(f"Failed to start process {process_id}")

            except Exception as e:
                self.logger.error(f"Error running command {cmd}: {str(e)}", exc_info=True)

    def start(self):
        """Start processing all configured flows."""
        self.logger.info("Starting Stream Filter Router...")
        
        # Check for existing processes
        self.logger.info("Checking for existing processes...")
        existing_processes = check_existing_processes(self.process_config_path)
        self.logger.info("\nExisting processes:\n" + existing_processes + "\n")
        
        self.logger.debug(f"Loaded {len(self.flows_config['flows'])} flows")
        self.logger.debug(f"Loaded {len(self.process_config)} process configurations")
        
        for flow_config in self.flows_config['flows']:
            name = flow_config['name']
            steps = flow_config['steps']
            self.logger.debug(f"Starting thread for flow '{name}': {steps}")
            threading.Thread(target=self._process_flow, args=(name, steps), daemon=True).start()
        
        self.logger.info("All flows started")

    def stop(self):
        """Stop all running processes and clean up."""
        with self._shutdown_lock:
            if self._is_shutting_down:
                return
            self._is_shutting_down = True
            
            self.logger.info("Stopping Stream Filter Router...")
            self.shutdown_event.set()

            # Stop all managed processes
            for process_id, process in list(self.running_processes.items()):
                try:
                    self.logger.debug(f"Stopping process {process_id}")
                    if process.stop():
                        self.logger.info(f"Process {process_id} stopped gracefully")
                    else:
                        self.logger.error(f"Failed to stop process {process_id}")
                except Exception as e:
                    self.logger.error(f"Error stopping process {process_id}: {str(e)}")

            self.logger.info("Stream Filter Router stopped")
            sys.exit(0)  # Ensure complete termination

    def get_process_states(self) -> List[Dict]:
        """
        Get state information for all running processes.
        
        Returns:
            list: List of process state dictionaries
        """
        return [process.get_state() for process in self.running_processes.values()]
