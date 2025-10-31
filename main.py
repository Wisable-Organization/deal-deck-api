#!/usr/bin/env python3
"""
DealDash - Simple entry point for Replit deployment
This starts both the FastAPI backend and Vite frontend development server.
"""

import subprocess
import threading
import time
import os
import signal
import sys
from pathlib import Path

def start_fastapi():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend on port 8000...")
    try:
        subprocess.run([
            "uvicorn", "api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ FastAPI failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 FastAPI stopped")

def start_vite():
    """Start the Vite frontend development server"""
    print("🎨 Starting Vite frontend on port 5173...")
    try:
        # Run Vite from root directory (package.json is here)
        subprocess.run([
            "npm", "run", "dev"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Vite failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 Vite stopped")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down servers...")
    sys.exit(0)

def main():
    """Main entry point"""
    print("🎯 DealDash - Starting development servers...")
    print("📋 Backend API: http://localhost:8000")
    print("📋 Frontend UI: http://localhost:5173")
    print("📋 API Docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop both servers\n")
    
    # Clean up any conflicting processes first
    print("🧹 Cleaning up any conflicting processes...")
    try:
        subprocess.run(["python", "cleanup.py"], check=False)
    except:
        pass
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Wait a moment for FastAPI to start
    time.sleep(3)
    
    # Start Vite in the main thread (so we can handle Ctrl+C properly)
    try:
        pass
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()
