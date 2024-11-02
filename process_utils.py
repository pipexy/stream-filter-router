"""
Process utilities for Stream Filter Router.
Handles process discovery and management.
"""

import subprocess
import re
import json
import logging
from typing import List, Dict, Set

logger = logging.getLogger("ProcessUtils")

def extract_commands_from_config(process_config_path: str) -> Set[str]:
    """
    Extract command names from process configuration.
    
    Args:
        process_config_path: Path to process.json
        
    Returns:
        set: Set of command names (e.g., ffmpeg, python)
    """
    commands = set()
    try:
        with open(process_config_path, 'r') as f:
            config = json.load(f)
            
        for process in config:
            if 'run' in process:
                for cmd in process['run']:
                    if cmd.startswith('shell://'):
                        # Extract the main command name (e.g., ffmpeg from ffmpeg -i ...)
                        cmd_name = cmd[7:].lstrip('/').split()[0]
                        commands.add(cmd_name)
                        
        return commands
    except Exception as e:
        logger.error(f"Error extracting commands from config: {str(e)}")
        return set()

def find_running_processes(command_names: Set[str]) -> List[Dict]:
    """
    Find running processes matching given command names.
    
    Args:
        command_names: Set of command names to look for
        
    Returns:
        list: List of process information dictionaries
    """
    processes = []
    
    try:
        # Get all running processes
        ps = subprocess.run(
            ['ps', '-eo', 'pid,ppid,user,%cpu,%mem,stat,start,time,command'],
            capture_output=True,
            text=True
        )
        
        if ps.returncode != 0:
            logger.error("Failed to get process list")
            return processes
            
        # Parse ps output
        lines = ps.stdout.split('\n')[1:]  # Skip header
        for line in lines:
            if not line.strip():
                continue
                
            parts = line.split(None, 8)  # Split into 9 parts (last part is command)
            if len(parts) < 9:
                continue
                
            cmd = parts[8]
            cmd_name = cmd.split()[0]
            
            # Check if this command matches any we're looking for
            for name in command_names:
                if cmd_name.endswith(name):
                    processes.append({
                        'pid': parts[0],
                        'ppid': parts[1],
                        'user': parts[2],
                        'cpu': parts[3],
                        'mem': parts[4],
                        'state': parts[5],
                        'start': parts[6],
                        'time': parts[7],
                        'command': cmd
                    })
                    break
                    
        return processes
    except Exception as e:
        logger.error(f"Error finding processes: {str(e)}")
        return []

def format_process_info(processes: List[Dict]) -> str:
    """
    Format process information for display.
    
    Args:
        processes: List of process information dictionaries
        
    Returns:
        str: Formatted process information
    """
    if not processes:
        return "No matching processes found."
        
    # Calculate column widths
    widths = {
        'pid': max(len(p['pid']) for p in processes),
        'user': max(len(p['user']) for p in processes),
        'cpu': max(len(p['cpu']) for p in processes),
        'mem': max(len(p['mem']) for p in processes),
        'start': max(len(p['start']) for p in processes),
        'time': max(len(p['time']) for p in processes)
    }
    
    # Create format string
    fmt = ("PID: {:<" + str(widths['pid']) + "} | "
           "USER: {:<" + str(widths['user']) + "} | "
           "CPU: {:>" + str(widths['cpu']) + "}% | "
           "MEM: {:>" + str(widths['mem']) + "}% | "
           "START: {:<" + str(widths['start']) + "} | "
           "TIME: {:<" + str(widths['time']) + "} | "
           "CMD: {}")
    
    # Format each process
    lines = []
    for p in processes:
        lines.append(fmt.format(
            p['pid'], p['user'], p['cpu'], p['mem'],
            p['start'], p['time'], p['command']
        ))
    
    return "\n".join(lines)

def check_existing_processes(config_path: str) -> str:
    """
    Check for existing processes based on configuration.
    
    Args:
        config_path: Path to process.json
        
    Returns:
        str: Formatted information about found processes
    """
    commands = extract_commands_from_config(config_path)
    if not commands:
        return "No commands found in configuration."
        
    processes = find_running_processes(commands)
    return format_process_info(processes)
