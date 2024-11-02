"""
Process management and control for Stream Filter Router.
Handles process lifecycle, data streaming, and health monitoring.
"""

import subprocess
import threading
import queue
import signal
import time
import os
import logging
from typing import Optional, Dict, Callable
from enum import Enum

class ProcessState(Enum):
    """Process states for lifecycle management."""
    INIT = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

class ManagedProcess:
    """
    Managed process with control, monitoring and data streaming.
    Provides clean lifecycle management and data passing.
    """
    
    def __init__(self, 
                 name: str,
                 command: str,
                 on_output: Optional[Callable[[str], None]] = None,
                 on_error: Optional[Callable[[str], None]] = None,
                 on_exit: Optional[Callable[[int], None]] = None):
        """
        Initialize managed process.
        
        Args:
            name: Process identifier
            command: Shell command to execute
            on_output: Callback for stdout data
            on_error: Callback for stderr data
            on_exit: Callback for process exit
        """
        self.name = name
        self.command = command
        self.process: Optional[subprocess.Popen] = None
        self.state = ProcessState.INIT
        self.exit_code: Optional[int] = None
        
        # Callbacks
        self.on_output = on_output
        self.on_error = on_error
        self.on_exit = on_exit
        
        # Data queues
        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()
        
        # Control
        self._stop_event = threading.Event()
        self._monitor_thread: Optional[threading.Thread] = None
        self._stdout_thread: Optional[threading.Thread] = None
        self._stderr_thread: Optional[threading.Thread] = None
        
        # Logging
        self.logger = logging.getLogger(f"Process.{name}")

    def _stream_output(self, pipe, queue_out: queue.Queue, is_stderr: bool = False):
        """Stream output from process pipe to queue."""
        try:
            while not self._stop_event.is_set():
                line = pipe.readline()
                if not line:
                    break
                    
                line = line.strip()
                queue_out.put(line)
                
                if is_stderr and self.on_error:
                    self.on_error(line)
                elif not is_stderr and self.on_output:
                    self.on_output(line)
                    
        except Exception as e:
            self.logger.error(f"Error reading {'stderr' if is_stderr else 'stdout'}: {str(e)}")
            
        finally:
            pipe.close()

    def _monitor(self):
        """Monitor process health and handle exit."""
        while not self._stop_event.is_set():
            if self.process.poll() is not None:
                self.exit_code = self.process.returncode
                self.state = ProcessState.STOPPED
                
                if self.on_exit:
                    self.on_exit(self.exit_code)
                    
                self.logger.info(f"Process exited with code {self.exit_code}")
                break
                
            time.sleep(0.1)

    def start(self) -> bool:
        """
        Start the managed process.
        
        Returns:
            bool: True if process started successfully
        """
        if self.state != ProcessState.INIT:
            self.logger.error(f"Cannot start process in state {self.state}")
            return False
            
        try:
            self.state = ProcessState.STARTING
            self.logger.info(f"Starting process: {self.command}")
            
            # Start process with pipes
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True,
                start_new_session=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Start monitoring threads
            self._monitor_thread = threading.Thread(
                target=self._monitor,
                daemon=True
            )
            self._stdout_thread = threading.Thread(
                target=self._stream_output,
                args=(self.process.stdout, self.stdout_queue),
                daemon=True
            )
            self._stderr_thread = threading.Thread(
                target=self._stream_output,
                args=(self.process.stderr, self.stderr_queue, True),
                daemon=True
            )
            
            self._monitor_thread.start()
            self._stdout_thread.start()
            self._stderr_thread.start()
            
            self.state = ProcessState.RUNNING
            self.logger.info(f"Process started with PID {self.process.pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start process: {str(e)}")
            self.state = ProcessState.ERROR
            return False

    def stop(self, timeout: int = 6) -> bool:
        """
        Stop the managed process.
        
        Args:
            timeout: Seconds to wait for graceful shutdown
            
        Returns:
            bool: True if process stopped successfully
        """
        if self.state not in [ProcessState.RUNNING, ProcessState.ERROR]:
            self.logger.error(f"Cannot stop process in state {self.state}")
            return False
            
        try:
            self.state = ProcessState.STOPPING
            self._stop_event.set()
            
            # Send SIGTERM to process group
            if self.process and self.process.poll() is None:
                self.logger.info(f"Sending SIGTERM to process group {self.process.pid}")
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                
            # Wait for process to exit
            stop_time = time.time() + timeout
            while time.time() < stop_time:
                if self.process.poll() is not None:
                    self.state = ProcessState.STOPPED
                    self.logger.info("Process stopped gracefully")
                    return True
                time.sleep(0.1)
                
            # Force kill if still running
            if self.process.poll() is None:
                self.logger.warning("Process did not stop gracefully, force killing")
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                self.process.wait()
                
            self.state = ProcessState.STOPPED
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping process: {str(e)}")
            return False

    def is_running(self) -> bool:
        """Check if process is running."""
        return (self.process is not None and 
                self.process.poll() is None and 
                self.state == ProcessState.RUNNING)

    def get_output(self, timeout: float = 0.1) -> Optional[str]:
        """
        Get next line from stdout queue.
        
        Args:
            timeout: Seconds to wait for data
            
        Returns:
            str: Output line or None if queue empty
        """
        try:
            return self.stdout_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_error(self, timeout: float = 0.1) -> Optional[str]:
        """
        Get next line from stderr queue.
        
        Args:
            timeout: Seconds to wait for data
            
        Returns:
            str: Error line or None if queue empty
        """
        try:
            return self.stderr_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_state(self) -> Dict:
        """
        Get process state information.
        
        Returns:
            dict: Process state details
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "pid": self.process.pid if self.process else None,
            "exit_code": self.exit_code,
            "command": self.command
        }
