#!/usr/bin/env python3
"""
Start backend with ngrok tunnel for remote access
"""
import os
import sys
import subprocess
import time
import requests
from urllib.parse import urlparse

# Try to install pyngrok if not available
try:
    from pyngrok import ngrok
except ImportError:
    print("Installing pyngrok...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok", "-q"])
    from pyngrok import ngrok

def start_backend_with_tunnel():
    """Start the FastAPI backend and create an ngrok tunnel"""
    
    # Start the backend server
    print("🚀 Starting FastAPI backend on port 8001...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"],
        cwd="d:\\CALOBLOOD\\Backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for backend to start
    time.sleep(3)
    
    # Create ngrok tunnel
    print("🌐 Creating ngrok tunnel...")
    try:
        public_url = ngrok.connect(8001, "http")
        print(f"\n✅ Backend is now publicly accessible at: {public_url}")
        print(f"\n📝 Share this URL with your friend's app:")
        print(f"   Backend URL: {public_url}")
        
        # Keep the tunnel alive
        print("\n💾 Tunnel is running. Press Ctrl+C to stop.\n")
        ngrok_process = ngrok.get_ngrok_process()
        ngrok_process.proc.wait()
        
    except Exception as e:
        print(f"❌ Error creating tunnel: {e}")
        backend_process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    start_backend_with_tunnel()
