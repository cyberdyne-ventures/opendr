import os
import psutil
import time
import logging
from datetime import datetime
import common.attributes as attr
from common.logger import check_logging_interval, enter_debug_logs
from typing import NoReturn

# Global counter for log lines written
log_line_count: int = 0

# Retrieve system details once
sid: str = attr.get_computer_sid()
hostname: str = attr.get_hostname()

def log_message(logger: logging.Logger, message: str) -> None:
  """Logs a message and updates the global line counter."""
  global log_line_count
  logger.info(message)
  log_line_count += 1  # Increment counter

def log_existing_processes(logger: logging.Logger) -> None:
  """Logs all currently running processes at script startup."""
  #log_message(logger, f"Logging all existing processes at startup on {hostname} with SID: {sid}")
  for proc in psutil.process_iter(attrs=['pid', 'name', 'exe', 'username', 'cmdline']):
    try:
      proc_info = proc.as_dict(attrs=['pid', 'name', 'username'])
      pid = proc_info.get('pid', 'N/A')
      proc_name: str = proc_info.get('name', 'Unknown')
      user: str = proc_info.get('username', 'N/A')

      # Handle cases where the parent process is None
      parent_pid, parent_name = "N/A", "N/A"
      parent: psutil.Process|None = proc.parent()
      if parent:  # Check if parent is not None
          parent_pid = parent.pid
          parent_name = parent.name()

      log_message(logger, f"timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"hostname: {hostname} | username: {user} | event: existing process | "
        f"pid: {pid} | name: {proc_name} | ppid: {parent_pid} | parent: {parent_name} | sid: {sid}")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
      continue  # Ignore processes that vanish before logging

def monitor_process_events(log_directory: str, ready_directory: str, interval: float=1.0) -> NoReturn:
  """Monitors process creation and termination events while tracking log lines written."""
  logger, last_minute = check_logging_interval(log_directory, ready_directory, "ProcessMonitor", "process", None, None)
  previous_processes: set[int] = set(psutil.pids())

  # Log all running processes at startup
  log_existing_processes(logger)

  while True:
    # # Check if the minute has changed to rotate the log file
    logger, last_minute = check_logging_interval(log_directory, ready_directory, "ProcessMonitor", "process", logger, last_minute)

    current_processes: set[int] = set(psutil.pids()) 
    created_processes = current_processes - previous_processes
    terminated_processes = previous_processes - current_processes

    # Log created processes
    for pid in created_processes:
      try:
        proc: psutil.Process = psutil.Process(pid)
        proc_info = proc.as_dict(attrs=['pid', 'name', 'username'])
        pid = proc_info.get('pid', 'N/A')
        proc_name: str = proc_info.get('name', 'Unknown')
        user: str = proc_info.get('username', 'N/A')

        # Handle cases where the parent process is None
        parent_pid, parent_name = "N/A", "N/A"
        parent: psutil.Process|None = proc.parent()
        if parent:  # Check if parent is not None
            parent_pid: int = parent.pid
            parent_name: str = parent.name()

        log_message(logger, f"timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
          f"hostname: {hostname} | username: {user} | event: process created | "
          f"pid: {pid} | name: {proc_name} | ppid: {parent_pid} | parent: {parent_name} | sid: {sid}"
        )
      except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

    # Log terminated processes
    for pid in terminated_processes:
      try:
        proc: psutil.Process = psutil.Process(pid)
        proc_info = proc.as_dict(attrs=['pid', 'name', 'username'])
        pid = proc_info.get('pid', 'N/A')
        proc_name: str = proc_info.get('name', 'Unknown')
        user: str = proc_info.get('username', 'N/A')
        # Handle cases where the parent process is None
        parent_pid, parent_name = "N/A", "N/A"
        parent: psutil.Process|None = proc.parent()
        if parent:  # Check if parent is not None
            parent_pid: int = parent.pid
            parent_name: str = parent.name()

        log_message(logger, f"timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"pid: {pid} | name: {proc_name} | hostname: {hostname} | ppid: {parent_pid} | parent: {parent_name} | username: {user} | sid: {sid}")
      except (psutil.NoSuchProcess, psutil.AccessDenied):
        log_message(logger, f"timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
          f"hostname: {hostname} | username: {user} | event: process terminated | "
          f"pid: {pid} | name: {proc_name} | ppid: {parent_pid} | parent: {parent_name} | sid: {sid}")
          #f"pid: {pid} | name: | hostname: | ppid: | parent: | username: | sid: {sid}")

    # Print the current running total of log lines every 10 seconds
    if int(time.time()) % 10 == 0:
      enter_debug_logs('process', f"Running total log lines written: {log_line_count}  \n")

    # Update the previous process set
    previous_processes = current_processes
    time.sleep(interval)

def run() -> NoReturn:
  log_directory: str = 'tmp-process'
  ready_directory: str = 'ready'
  debug_generator_directory: str = 'debuggeneratorlogs'
  os.makedirs(debug_generator_directory, exist_ok=True)
  os.makedirs(log_directory, exist_ok=True)
  os.makedirs(ready_directory, exist_ok=True)
  # Run the monitor with a 0.1 second interval
  monitor_process_events(log_directory, ready_directory, interval=0.1)

run()