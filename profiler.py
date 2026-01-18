import os
import subprocess
import sys
import time  # New import for the delay

def setup():
    print("🛠️ Profiler: Initializing Ruru-CLI...")
    
    # 1. Create the requested log directory
    log_path = os.path.expanduser("~/ruru1901/logs")
    os.makedirs(log_path, exist_ok=True)
    
    print(f"📂 Created log directory at {log_path}")
    print("✅ System mapping complete.")
    print("\n💥 Task complete. Profiler is now self-destructing and clearing the screen in 5 seconds...")
    
    # 2. Self-destruction (Delete the file)
    try:
        if os.path.exists(__file__):
            os.remove(__file__)
    except Exception:
        pass
    time.sleep(5)
    os.system('clear' if os.name == 'posix' else 'cls')

if __name__ == "__main__":
    setup()
