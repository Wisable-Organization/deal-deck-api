#!/usr/bin/env python3
"""
Cleanup script to kill any conflicting processes
"""

import subprocess
import os

def kill_processes():
    """Kill any processes that might be conflicting"""
    print("🧹 Cleaning up conflicting processes...")
    
    # Kill any uvicorn processes
    try:
        subprocess.run(["pkill", "-f", "uvicorn"], check=False)
        print("✅ Killed uvicorn processes")
    except:
        print("ℹ️  No uvicorn processes found")
    
    # Kill any node processes
    try:
        subprocess.run(["pkill", "-f", "node"], check=False)
        print("✅ Killed node processes")
    except:
        print("ℹ️  No node processes found")
    
    # Kill any tsx processes
    try:
        subprocess.run(["pkill", "-f", "tsx"], check=False)
        print("✅ Killed tsx processes")
    except:
        print("ℹ️  No tsx processes found")
    
    # Kill any vite processes
    try:
        subprocess.run(["pkill", "-f", "vite"], check=False)
        print("✅ Killed vite processes")
    except:
        print("ℹ️  No vite processes found")
    
    # Kill any processes on port 5000
    try:
        result = subprocess.run(["lsof", "-ti:5000"], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(["kill", "-9", pid], check=False)
            print("✅ Killed processes on port 5000")
    except:
        print("ℹ️  No processes found on port 5000")
    
    # Kill any processes on port 5173
    try:
        result = subprocess.run(["lsof", "-ti:5173"], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(["kill", "-9", pid], check=False)
            print("✅ Killed processes on port 5173")
    except:
        print("ℹ️  No processes found on port 5173")
    
    # Kill any processes on port 8000
    try:
        result = subprocess.run(["lsof", "-ti:8000"], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(["kill", "-9", pid], check=False)
            print("✅ Killed processes on port 8000")
    except:
        print("ℹ️  No processes found on port 8000")
    
    print("✅ Cleanup complete!")

if __name__ == "__main__":
    kill_processes()
