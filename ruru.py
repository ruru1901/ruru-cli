import subprocess
import sys
import os
import shlex
import time
import itertools
import re  # Added for parsing the command
from datetime import datetime

# --- CONFIG ---
LOG_DIR = os.path.expanduser("~/ruru1901/logs")
LOG_FILE = os.path.join(LOG_DIR, "history.log")

def ensure_logs():
    os.makedirs(LOG_DIR, exist_ok=True)

def spinning_cursor():
    return itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

# --- THE BRAIN (Optimized for Speed) ---
def ask_gemini(task):
    # Shortened prompt for faster response
    prompt = f"""
    Expert Linux CLI. Task: '{task}'
    Provide:
    Task Name: {task}
    Command: 1 [command] # desc
    Function: [desc]
    Risk Level: [Low/Mid/High]
    Why: [desc]
    """
    
    spinner = spinning_cursor()
    print("\n🧠 Ruru Brain: Thinking...", end=" ", flush=True)
    
    try:
        # Using a 10s timeout to keep it snappy
        output = subprocess.check_output(["gemini", prompt], stderr=subprocess.STDOUT, text=True, timeout=10)
        print("Done!")
        return output.strip()
    except Exception:
        return None

# --- THE HAND (Handles Execution) ---
def execute_hidden(command):
    # Clean the command (remove the '1 ' and comments if AI included them)
    cmd_clean = re.sub(r'^\d+\s+', '', command.split('#')[0]).strip()
    
    if "sudo" in cmd_clean:
        print("\n🔐 Ruru needs sudo privileges:")
        subprocess.run(["sudo", "-v"]) 

    spinner = spinning_cursor()
    print(f"\n🚀 RURU HAND: Running [{cmd_clean}]...")
    
    try:
        process = subprocess.Popen(
            shlex.split(cmd_clean),
            stdout=subprocess.PIPE, # Changed to PIPE so we can show output if needed
            stderr=subprocess.PIPE,
            text=True
        )

        while process.poll() is None:
            sys.stdout.write(f"\r{next(spinner)} Working... ")
            sys.stdout.flush()
            time.sleep(0.05) # Faster spinner for "feel"
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            subprocess.run(["hash", "-r"])
            sys.stdout.write("\r✅ Done! Task successful.          \n")
            if stdout: print(f"\nOutput:\n{stdout}")
            return "SUCCESS"
        else:
            sys.stdout.write("\r❌ Task Failed!                          \n")
            print(f"⚠️ Error: {stderr.strip()}")
            return "FAILED"
    except Exception as e:
        print(f"\r❌ Error: {str(e)}")
        return "ERROR"

# --- HISTORY & CACHE ---
def history_menu():
    ensure_logs()
    if not os.path.exists(LOG_FILE):
        print("Empty history.")
        return
    # ... (Keep your existing history_menu logic here) ...

def check_cache(task_name):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            content = f.read()
            if task_name in content and "SUCCESS" in content:
                return True
    return False

# --- THE FLOW ---
def run_flow(task_description):
    # 1. Fast Cache Check
    if check_cache(task_description):
        fast_path = input(f"⚡ Ruru remembers this. Run quickly? (y/n): ")
        if fast_path.lower() == 'y':
            # Ask AI just for the command (very fast)
            analysis = ask_gemini(f"Give ONLY the raw linux command for: {task_description}")
            if analysis:
                execute_hidden(analysis)
                return

    # 2. Normal AI Analysis
    analysis = ask_gemini(task_description)
    if not analysis or "Brain Offline" in analysis:
        print("❌ Brain unavailable.")
        return

    print("\n" + "="*60 + "\n" + analysis + "\n" + "="*60)

    # 3. Extract Command and Confirm
    try:
        # Look for the line that starts with '1 ' in the Command section
        cmd_line = [line for line in analysis.split('\n') if line.strip().startswith('1 ')][0]
        
        confirm = input("\nDo you accept this proposal? (y/n): ").lower()
        if confirm == 'y':
            status = execute_hidden(cmd_line)
            ensure_logs()
            with open(LOG_FILE, "a") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {task_description} | {status}\n")
    except Exception:
        print("❌ Could not parse command from Brain.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ruru <task description> | ruru history")
        sys.exit(1)

    cmd_arg = sys.argv[1]
    if cmd_arg in ["history", "historia"]:
        history_menu()
    else:
        # Join all arguments: "check nmap version"
        full_task = " ".join(sys.argv[1:])
        run_flow(full_task)
