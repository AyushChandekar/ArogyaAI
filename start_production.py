#!/usr/bin/env python3
"""
Production startup script for ArogyaAI
Handles starting multiple services in the correct order
"""

import os
import sys
import time
import subprocess
import signal
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ProductionManager:
    def __init__(self):
        self.processes = []
        self.rasa_process = None
        self.actions_process = None
        self.main_process = None
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()
        sys.exit(0)
    
    def check_requirements(self):
        """Check if all required files exist"""
        required_files = [
            'clean_disease_data.csv',
            'config.yml',
            'domain.yml',
            'endpoints.yml'
        ]
        
        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if missing_files:
            logger.error(f"Missing required files: {missing_files}")
            return False
        
        return True
    
    def wait_for_service(self, url, timeout=60, service_name="Service"):
        """Wait for a service to be available"""
        import requests
        
        logger.info(f"Waiting for {service_name} to be available at {url}")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    logger.info(f"{service_name} is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        logger.error(f"{service_name} failed to start within {timeout} seconds")
        return False
    
    def start_rasa_server(self):
        """Start Rasa server"""
        logger.info("Starting Rasa server...")
        
        cmd = [
            sys.executable, "-m", "rasa", "run",
            "--enable-api",
            "--cors", "*",
            "--port", "5005"
        ]
        
        try:
            self.rasa_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.processes.append(self.rasa_process)
            
            # Wait for Rasa to be ready
            if self.wait_for_service("http://localhost:5005", service_name="Rasa server"):
                return True
            else:
                self.rasa_process.terminate()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start Rasa server: {e}")
            return False
    
    def start_rasa_actions(self):
        """Start Rasa actions server"""
        logger.info("Starting Rasa actions server...")
        
        cmd = [
            sys.executable, "-m", "rasa", "run", "actions",
            "--port", "5055"
        ]
        
        try:
            self.actions_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.processes.append(self.actions_process)
            
            # Wait a bit for actions server to start
            time.sleep(5)
            
            # Check if process is still running
            if self.actions_process.poll() is None:
                logger.info("Rasa actions server started successfully")
                return True
            else:
                logger.error("Rasa actions server failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start Rasa actions server: {e}")
            return False
    
    def start_main_application(self):
        """Start the main FastAPI application"""
        logger.info("Starting main FastAPI application...")
        
        # Choose which server to run based on environment
        app_mode = os.getenv('APP_MODE', 'backend')  # backend, webhook, or app
        
        if app_mode == 'webhook':
            cmd = [sys.executable, "webhook_server.py"]
        elif app_mode == 'app':
            cmd = [sys.executable, "app.py"]
        else:  # default to backend
            cmd = [sys.executable, "backend.py"]
        
        try:
            self.main_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.processes.append(self.main_process)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start main application: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor all processes and restart if needed"""
        logger.info("Monitoring processes...")
        
        while True:
            try:
                # Check Rasa server
                if self.rasa_process and self.rasa_process.poll() is not None:
                    logger.error("Rasa server died, attempting restart...")
                    self.start_rasa_server()
                
                # Check actions server
                if self.actions_process and self.actions_process.poll() is not None:
                    logger.error("Rasa actions server died, attempting restart...")
                    self.start_rasa_actions()
                
                # Check main application
                if self.main_process and self.main_process.poll() is not None:
                    logger.error("Main application died, attempting restart...")
                    self.start_main_application()
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                break
    
    def shutdown(self):
        """Shutdown all processes gracefully"""
        logger.info("Shutting down all services...")
        
        for process in self.processes:
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning("Process didn't terminate gracefully, killing...")
                    process.kill()
                except Exception as e:
                    logger.error(f"Error terminating process: {e}")
    
    def start_all(self):
        """Start all services in the correct order"""
        logger.info("🏥 Starting ArogyaAI Production Services...")
        
        # Check requirements
        if not self.check_requirements():
            logger.error("Requirements check failed")
            return False
        
        # Start services in order
        success = True
        
        # 1. Start Rasa server (if not disabled)
        if os.getenv('DISABLE_RASA', '').lower() != 'true':
            success &= self.start_rasa_server()
            if success:
                success &= self.start_rasa_actions()
        
        # 2. Start main application
        if success:
            success &= self.start_main_application()
        
        if success:
            logger.info("🚀 All services started successfully!")
            # Monitor processes (this will run until interrupted)
            self.monitor_processes()
        else:
            logger.error("❌ Failed to start some services")
            self.shutdown()
            return False
        
        return True

def main():
    """Main entry point"""
    manager = ProductionManager()
    
    try:
        success = manager.start_all()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down...")
        manager.shutdown()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        manager.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    main()