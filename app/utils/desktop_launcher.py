"""
Reusable desktop launcher for Python web apps bundled with PyInstaller.

Handles:
- Single-instance detection (prevents duplicate processes)
- Dynamic port allocation (works even if default port busy)
- Chrome subprocess management (Python exits when Chrome closes)
- Clean shutdown (no ghost processes, no stuck ports)

Usage:
    from app.utils.desktop_launcher import DesktopLauncher
    
    launcher = DesktopLauncher(
        app_name="HappyManPos",
        exe_name="HappyManPos.exe",
        preferred_port=8000,
        app_data_dir=get_app_data_dir(),
    )
    
    launcher.run(fastapi_app)
"""

import os
import sys
import time
import socket
import logging
import threading
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional

import psutil
import uvicorn


logger = logging.getLogger(__name__)


class DesktopLauncher:
    """
    Launches a FastAPI web app as a desktop application.
    Handles Chrome lifecycle, single-instance checks, and clean shutdown.
    """
    
    def __init__(
        self,
        app_name: str,
        exe_name: str,
        preferred_port: int,
        app_data_dir: Path,
        max_port_tries: int = 20,
        chrome_startup_delay: float = 3.0,
    ):
        self.app_name = app_name
        self.exe_name = exe_name
        self.preferred_port = preferred_port
        self.app_data_dir = app_data_dir
        self.max_port_tries = max_port_tries
        self.chrome_startup_delay = chrome_startup_delay
        self.chrome_process: Optional[subprocess.Popen] = None
    
    # ============================================================
    # SINGLE INSTANCE CHECK
    # ============================================================
    
    def is_already_running(self) -> bool:
        """
        Check if another instance is truly running (not just dying).
        
        Verifies by:
        1. Finding candidate processes
        2. Waiting briefly
        3. Confirming they're still alive
        4. Checking they have the expected characteristics
        """
        current_pid = os.getpid()
        
        try:
            current_exe = Path(sys.executable).resolve()
        except Exception as e:
            logger.warning(f"Can't resolve own exe: {e}")
            return False
        
        logger.info(f"Checking duplicates. Current: PID {current_pid}, exe {current_exe}")
        
        # First scan: find candidates
        candidates = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['pid'] == current_pid:
                    continue
                if proc.info['name'] != self.exe_name:
                    continue
                
                proc_exe = proc.info.get('exe')
                if proc_exe:
                    try:
                        if Path(proc_exe).resolve() == current_exe:
                            candidates.append(proc.info['pid'])
                            logger.info(f"Candidate: PID {proc.info['pid']}")
                    except Exception:
                        continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not candidates:
            logger.info("No candidates found")
            return False
        
        # Wait briefly for any dying processes to actually die
        logger.info(f"Found {len(candidates)} candidate(s), verifying they're truly alive...")
        time.sleep(1.5)
        
        # Verify each candidate is still alive and functional
        alive_count = 0
        for pid in candidates:
            if self._is_process_alive(pid):
                alive_count += 1
                logger.info(f"PID {pid} is CONFIRMED alive")
            else:
                logger.info(f"PID {pid} was dying, now gone")
        
        logger.info(f"Confirmed {alive_count} alive instance(s)")
        return alive_count > 0


    def _is_process_alive(self, pid: int) -> bool:
        """
        Check if a process is truly alive and functional.
        Returns False if it's a zombie or in the process of dying.
        """
        try:
            proc = psutil.Process(pid)
            
            # Check it still exists
            if not proc.is_running():
                return False
            
            # Check it's not a zombie
            status = proc.status()
            if status in (psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD):
                return False
            
            # Try to get CPU time - fails if process is really dying
            try:
                proc.cpu_times()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return False
            
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def show_already_running_message(self):
        """User-facing message when duplicate detected."""
        print()
        print("=" * 60)
        print(f"{self.app_name} is already running")
        print("=" * 60)
        print()
        print("Options:")
        print("  1. Look for the Chrome window on your taskbar")
        print("  2. Or open Task Manager (Ctrl+Shift+Esc)")
        print(f"     Find '{self.exe_name}' processes")
        print("     End them, then try again")
        print()
        print("=" * 60)
        print()
        self._wait_or_exit()
    
    # ============================================================
    # PORT MANAGEMENT
    # ============================================================
    
    def find_free_port(self) -> int:
        """
        Find an available port starting from preferred_port.
        
        Raises RuntimeError if no port available in range.
        """
        for port in range(self.preferred_port, self.preferred_port + self.max_port_tries):
            if self._is_port_free(port):
                logger.info(f"Port {port} available")
                return port
        
        raise RuntimeError(
            f"No free port found in range "
            f"{self.preferred_port}-{self.preferred_port + self.max_port_tries}"
        )
    
    def _is_port_free(self, port: int) -> bool:
        """Check if a specific port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return True
        except OSError:
            return False
    
    # ============================================================
    # CHROME LIFECYCLE
    # ============================================================
    
    def _find_chrome(self) -> Optional[str]:
        """Find Chrome executable on the system."""
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ]
        
        for path in chrome_paths:
            if Path(path).exists():
                logger.info(f"Chrome found: {path}")
                return path
        
        logger.warning("Chrome not found at standard locations")
        return None
    
    def _get_chrome_profile_dir(self) -> Path:
        """
        Get dedicated Chrome profile directory for this app.
        Critical for subprocess tracking to work reliably.
        """
        profile_dir = self.app_data_dir / "chrome_profile"
        profile_dir.mkdir(parents=True, exist_ok=True)
        return profile_dir
    
    def _launch_chrome(self, url: str) -> Optional[subprocess.Popen]:
        """
        Launch Chrome in app mode as subprocess.
        Returns Popen object or None if Chrome not available.
        """
        chrome_exe = self._find_chrome()
        
        if not chrome_exe:
            logger.warning("Chrome not available, falling back to default browser")
            logger.warning("Note: ghost process prevention won't work with default browser")
            webbrowser.open(url)
            return None
        
        profile_dir = self._get_chrome_profile_dir()
        
        cmd = [
            chrome_exe,
            f'--app={url}',
            f'--user-data-dir={profile_dir}',
            '--new-window',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-features=TranslateUI',
        ]
        
        logger.info(f"Launching Chrome: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(cmd)
            logger.info(f"Chrome subprocess PID: {process.pid}")
            return process
        except Exception as e:
            logger.error(f"Failed to launch Chrome: {e}", exc_info=True)
            webbrowser.open(url)
            return None
    
    def _chrome_watcher_thread(self, url: str):
        """
        Thread that:
        1. Waits for backend to start
        2. Launches Chrome
        3. Waits for Chrome to close
        4. Kills Python process cleanly
        """
        # Wait for backend to be ready
        logger.info(f"Waiting {self.chrome_startup_delay}s for backend to start")
        time.sleep(self.chrome_startup_delay)
        
        # Launch Chrome
        self.chrome_process = self._launch_chrome(url)
        
        if self.chrome_process is None:
            # Fallback browser used - we can't track it
            # Keep Python running (user must close manually)
            logger.info("Using fallback browser - no auto-shutdown")
            return
        
        # Wait for Chrome window to close
        logger.info("Watching Chrome process - will exit when it closes")
        try:
            self.chrome_process.wait()
        except Exception as e:
            logger.error(f"Error watching Chrome: {e}", exc_info=True)
        
        # Chrome closed - clean shutdown
        logger.info("Chrome window closed - shutting down backend")
        logger.info("=" * 60)
        logger.info(f"{self.app_name} session ended")
        logger.info("=" * 60)
        
        # Give logger time to flush
        time.sleep(0.5)
        
        # Force exit the Python process
        os._exit(0)
    
    # ============================================================
    # SHUTDOWN HELPERS
    # ============================================================
    
    def _wait_or_exit(self):
        """Wait for user input if possible, else sleep briefly."""
        try:
            input("Press Enter to close...")
        except (RuntimeError, EOFError):
            # No stdin available (bundled with console=False)
            time.sleep(10)
        sys.exit(0)
    
    def cleanup_chrome(self):
        """Kill Chrome subprocess if still running."""
        if self.chrome_process and self.chrome_process.poll() is None:
            logger.info("Terminating Chrome subprocess")
            try:
                self.chrome_process.terminate()
                self.chrome_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Chrome didn't terminate, killing")
                self.chrome_process.kill()
            except Exception as e:
                logger.error(f"Error terminating Chrome: {e}")
    
    # ============================================================
    # MAIN RUN METHOD
    # ============================================================
    
    def run(self, fastapi_app):
      logger.info("=" * 60)
      logger.info(f"{self.app_name} launcher starting")
      logger.info("=" * 60)
      logger.info(f"PID: {os.getpid()}")
      logger.info(f"Bundled: {getattr(sys, 'frozen', False)}")
      
      # Find available port (handles both legit instances and ghosts naturally)
      try:
          port = self.find_free_port()
      except RuntimeError as e:
          logger.error(str(e))
          print(f"\nError: {e}")
          self._wait_or_exit()
          return
      
      url = f"http://localhost:{port}/"
      logger.info(f"App will be available at: {url}")
      
      # Start Chrome watcher thread
      chrome_thread = threading.Thread(
          target=self._chrome_watcher_thread,
          args=(url,),
          daemon=False,
          name="ChromeWatcher"
      )
      chrome_thread.start()
      
      # Start uvicorn
      logger.info(f"Starting uvicorn on port {port}")
      try:
          uvicorn.run(
              fastapi_app,
              host="127.0.0.1",
              port=port,
              log_level="info",
              log_config=None,
          )
      except KeyboardInterrupt:
          logger.info("Shutdown via Ctrl+C")
      except Exception as e:
          logger.error(f"Uvicorn error: {e}", exc_info=True)
      finally:
          self.cleanup_chrome()
          logger.info("Launcher exited")