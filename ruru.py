import subprocess
import sys
import os
import shlex
import time
import itertools
import re
from datetime import datetime

# --- CONFIG ---
DEBUG = True  # SET THIS TO TRUE to see exactly why the Brain fails
LOG_DIR = os.path.expanduser("~/ruru1901/logs")
LOG_FILE = os.path.join(LOG_DIR, "history.log")

def ensure_logs():
    os.makedirs(LOG_DIR, exist_ok=True)

def spinning_cursor():
    return itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

# --- THE BRAIN (Now with Debug + Cleaning) ---
def ask_gemini(task):
    prompt = f"Expert Linux CLI. Task: '{task}'. Provide: Task Name, Command (starting with '1 '), Function, Risk Level, and Why."
    
    spinner = spinning_cursor()
    print("\n🧠 Ruru Brain: Thinking...", end=" ", flush=True)
    
    try:
        # Popen is more stable for capturing both stdout and stderr
        process = subprocess.Popen(
            ["gemini", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        while process.poll() is None:
            sys.stdout.write(f"\r{next(spinner)} Thinking... ")
            sys.stdout.flush()
            time.sleep(0.1)

        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print("Done!")
            # ⚡ CRITICAL FIX: Ignore "Loaded cached credentials" lines
            clean_output = "\n".join([line for line in stdout.split('\n') if "credentials" not in line.lower()])
            return clean_output.strip()
        else:
            print("\n❌ Brain Connection Error.")
            if DEBUG:
                print(f"\n--- DEBUG INFO ---")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                print(f"------------------")
            return None

    except Exception as e:
        print(f"\n❌ System Error: {str(e)}")
        return None

# --- THE HAND (Fixed for Universal Output) ---
def execute_hidden(command):
    # Strip leading '1 ', trailing comments, and whitespace
    cmd_clean = re.sub(r'^\d+\s+', '', command.split('#')[0]).strip()
    
    if "sudo" in cmd_clean:
        print("\n🔐 Ruru needs sudo privileges:")
        subprocess.run(["sudo", "-v"]) 

    spinner = spinning_cursor()
    print(f"\n🚀 RURU HAND: Running [{cmd_clean}]...")
    
    try:
        process = subprocess.Popen(
            shlex.split(cmd_clean),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        while process.poll() is None:
            sys.stdout.write(f"\r{next(spinner)} Working... ")
            sys.stdout.flush()
            time.sleep(0.05)
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            subprocess.run(["hash", "-r"])
            sys.stdout.write("\r✅ Task Successful!          \n")
            if stdout: 
                print(f"\n--- OUTPUT ---\n{stdout.strip()}\n--------------")
            return "SUCCESS"
        else:
            sys.stdout.write("\r❌ Task Failed!                          \n")
            print(f"⚠️ Error Detail: {stderr.strip()}")
            return "FAILED"
    except Exception as e:
        print(f"\r❌ Execution Error: {str(e)}")
        return "ERROR"

# --- THE FLOW ---
def run_flow(task_description):
    # (Optional) Cache check can go here
    
    analysis = ask_gemini(task_description)
    if not analysis:
        print("❌ Brain unavailable. Check your connection or login.")
        return

    print("\n" + "="*60 + "\n" + analysis + "\n" + "="*60)

    try:
        # Regex to find the line starting with '1 '
        match = re.search(r'^1\s+(.*)', analysis, re.MULTILINE)
        if match:
            cmd_line = match.group(0)
            confirm = input("\nDo you accept this proposal? (y/n): ").lower()
            if confirm == 'y':
                status = execute_hidden(cmd_line)
                ensure_logs()
                with open(LOG_FILE, "a") as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {task_description} | {status}\n")
        else:
            print("❌ Brain provided an invalid command format.")
    except Exception as e:
        if DEBUG: print(f"Parser Error: {e}")
        print("❌ Error processing the Brain's response.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ruru <task description> | ruru history")
        sys.exit(1)

    cmd_arg = sys.argv[1]
    if cmd_arg in ["history", "historia"]:
        # history_menu() logic here
        pass
    else:
        full_task = " ".join(sys.argv[1:])
        run_flow(full_task)
