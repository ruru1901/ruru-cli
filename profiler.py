import os
import subprocess
import sys

def setup():
    print("🛠️ Profiler: Initializing Ruru-CLI...")
    
    # Create the requested log directory
    log_path = os.path.expanduser("~/ruru1901/logs")
    os.makedirs(log_path, exist_ok=True)
    
    print(f"📂 Created log directory at {log_path}")
    print("💥 Task complete. Profiler is now self-destructing...")
    
    # Self-destruction
    if os.path.exists(__file__):
        os.remove(__file__)

if __name__ == "__main__":
    setup()
