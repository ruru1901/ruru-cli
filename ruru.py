import subprocess
import sys
import os
import shlex
import time
import itertools
import re
import json
from datetime import datetime
from brain import analyze_task

# --- CONFIG ---
DEBUG = True  # SET THIS TO TRUE to see exactly why the Brain fails
LOG_DIR = os.path.expanduser("~/ruru1901/logs")
LOG_FILE = os.path.join(LOG_DIR, "history.log")

def ensure_logs():
    os.makedirs(LOG_DIR, exist_ok=True)

def spinning_cursor():
    return itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

def init_config():
    config_dir = os.path.expanduser("~/.ruru")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.json")

    print("🛠️ Ruru Initialization Menu")
    print("Choose AI backend:")
    print("1. Groq")
    print("2. OpenRouter")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        backend = "groq"
        model = input("Enter Groq model (default llama3-70b-8192): ").strip() or "llama3-70b-8192"
        config = {"ai_backend": backend, "groq_model": model}
    elif choice == "2":
        backend = "openrouter"
        model = input("Enter OpenRouter model (default meta-llama/llama-3-70b-instruct): ").strip() or "meta-llama/llama-3-70b-instruct"
        config = {"ai_backend": backend, "openrouter_model": model}
    else:
        print("Invalid choice, defaulting to Groq.")
        config = {"ai_backend": "groq", "groq_model": "llama3-70b-8192"}

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    print(f"✅ Config saved to {config_path}")



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

    spinner = spinning_cursor()
    print("\n🧠 Ruru Brain: Thinking...", end=" ", flush=True)

    analysis = analyze_task(task_description)
    if not analysis:
        print("❌ Brain unavailable. Check your API key and connection.")
        return

    print("Done!")

    print("\n" + "="*60)
    print(f"Command: {analysis['command']}")
    print(f"Risk: {analysis['risk']}")
    print(f"Explanation: {analysis['explanation']}")
    if analysis['warning']:
        print(f"Warning: {analysis['warning']}")
    print("="*60)

    try:
        cmd_line = analysis['command']
        confirm = input("\nDo you accept this proposal? (y/n): ").lower()
        if confirm == 'y':
            status = execute_hidden(cmd_line)
            ensure_logs()
            with open(LOG_FILE, "a") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {task_description} | {status}\n")
        else:
            print("❌ Proposal rejected.")
    except Exception as e:
        if DEBUG: print(f"Parser Error: {e}")
        print("❌ Error processing the Brain's response.")

if __name__ == "__main__":
    config_path = os.path.expanduser("~/.ruru/config.json")
    if not os.path.exists(config_path):
        init_config()

    if len(sys.argv) < 2:
        print("Usage: ruru <task description> | ruru history | ruru init")
        sys.exit(1)

    cmd_arg = sys.argv[1]
    if cmd_arg in ["history", "historia"]:
        # history_menu() logic here
        pass
    elif cmd_arg == "init":
        init_config()
    else:
        full_task = " ".join(sys.argv[1:])
        run_flow(full_task)
