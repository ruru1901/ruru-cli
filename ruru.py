import subprocess
import sys
import os
import shlex
import time
import itertools
import re
import json
from datetime import datetime
from brain import analyze_task, explain_command

# --- CONFIG ---
DEBUG = True  # SET THIS TO TRUE to see exactly why the Brain fails
LOG_DIR = os.path.expanduser("~/ruru1901/logs")
LOG_FILE = os.path.join(LOG_DIR, "history.log")
LAST_JSON = os.path.expanduser("~/.ruru/last.json")

# --- COLORS ---
COLORS = {
    'SUCCESS': '\033[92m',
    'FAILED': '\033[91m',
    'ERROR': '\033[93m',
    'HIGH-RISK-ACCEPTED': '\033[95m',
    'HIGH-RISK-REJECTED': '\033[95m',
    'DRY-RUN': '\033[96m',
    'END': '\033[0m'
}

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
        api_key = input("Enter your Groq API key: ").strip()
        if api_key:
            print(f"Please set the environment variable: export GROQ_API_KEY={api_key}")
        config = {"ai_backend": backend, "groq_model": model}
    elif choice == "2":
        backend = "openrouter"
        model = input("Enter OpenRouter model (default meta-llama/llama-3-70b-instruct): ").strip() or "meta-llama/llama-3-70b-instruct"
        api_key = input("Enter your OpenRouter API key: ").strip()
        if api_key:
            print(f"Please set the environment variable: export OPENROUTER_API_KEY={api_key}")
        config = {"ai_backend": backend, "openrouter_model": model}
    else:
        print("Invalid choice, defaulting to Groq.")
        api_key = input("Enter your Groq API key: ").strip()
        if api_key:
            print(f"Please set the environment variable: export GROQ_API_KEY={api_key}")
        config = {"ai_backend": "groq", "groq_model": "llama3-70b-8192"}

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    print(f"✅ Config saved to {config_path}")

def show_history(clear=False, last=None):
    if not os.path.exists(LOG_FILE):
        print("No history log found.")
        return

    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()

    if not lines:
        print("History log is empty.")
        return

    if clear:
        confirm = input("Are you sure you want to clear the history? (y/n): ").lower()
        if confirm == 'y':
            open(LOG_FILE, 'w').close()
            print("History cleared.")
        return

    entries = []
    for line in lines:
        if line.strip():
            parts = line.strip().split(' | ', 1)
            if len(parts) == 2:
                left, status = parts
                timestamp_task = left[1:-1]  # remove [ ]
                ts_task_parts = timestamp_task.split('] ', 1)
                if len(ts_task_parts) == 2:
                    timestamp, task = ts_task_parts
                else:
                    timestamp = ts_task_parts[0]
                    task = ''
                entries.append((timestamp, task, status))

    if last:
        entries = entries[-last:]

    print(f"{'Timestamp':<20} {'Task':<30} {'Status'}")
    print('-' * 80)
    for ts, task, stat in entries:
        color = COLORS.get(stat, '')
        print(f"{ts:<20} {task:<30} {color}{stat}{COLORS['END']}")

def undo():
    if not os.path.exists(LAST_JSON):
        print("Nothing to undo. No previous command found.")
        return

    with open(LAST_JSON, 'r') as f:
        data = json.load(f)

    cmd = data.get('command')
    if not cmd:
        print("Nothing to undo. No previous command found.")
        return

    task = f"What is the safe undo or reverse command for this Linux command: {cmd}"
    run_flow(task)

def switch_backend():
    config_path = os.path.expanduser("~/.ruru/config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)

    current_backend = config.get('ai_backend')
    current_model = config.get(f"{current_backend}_model")
    print(f"Current backend: {current_backend} ({current_model})")
    print("Choose new backend:")
    print("1. Groq")
    print("2. OpenRouter")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        backend = "groq"
        model = input(f"Enter Groq model (current: {current_model or 'llama3-70b-8192'}): ").strip() or (current_model or "llama3-70b-8192")
    elif choice == "2":
        backend = "openrouter"
        model = input(f"Enter OpenRouter model (current: {current_model or 'meta-llama/llama-3-70b-instruct'}): ").strip() or (current_model or "meta-llama/llama-3-70b-instruct")
    else:
        print("Invalid choice.")
        return

    config['ai_backend'] = backend
    config[f"{backend}_model"] = model
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    print(f"Switched to {backend} using {model}.")



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
            # Save last command
            with open(LAST_JSON, 'w') as f:
                json.dump({'command': cmd_clean}, f)
            return "SUCCESS"
        else:
            sys.stdout.write("\r❌ Task Failed!                          \n")
            print(f"⚠️ Error Detail: {stderr.strip()}")
            return "FAILED"
    except Exception as e:
        print(f"\r❌ Execution Error: {str(e)}")
        return "ERROR"

# --- THE FLOW ---
def run_flow(task_description, dry=False):
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

    if dry:
        print("[DRY RUN] Command not executed.")
        ensure_logs()
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {task_description} | DRY-RUN\n")
        return

    try:
        if analysis['risk'] == 'High':
            print("This is a HIGH RISK command. To confirm, type the command exactly:")
            user_input = input("> ").strip()
            if user_input == analysis['command'].strip():
                status = execute_hidden(analysis['command'])
                log_status = "HIGH-RISK-ACCEPTED"
            else:
                print("Aborted. Command not executed.")
                status = "HIGH-RISK-REJECTED"
                log_status = "HIGH-RISK-REJECTED"
        else:
            cmd_line = analysis['command']
            confirm = input("\nDo you accept this proposal? (y/n): ").lower()
            if confirm == 'y':
                status = execute_hidden(cmd_line)
                log_status = status
            else:
                print("❌ Proposal rejected.")
                return

        ensure_logs()
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {task_description} | {log_status}\n")
    except Exception as e:
        if DEBUG: print(f"Parser Error: {e}")
        print("❌ Error processing the Brain's response.")

if __name__ == "__main__":
    config_path = os.path.expanduser("~/.ruru/config.json")
    if not os.path.exists(config_path):
        init_config()

    if len(sys.argv) < 2:
        print("Usage: ruru <task> | ruru history [--clear|--last N] | ruru undo | ruru switch | ruru explain <cmd> | ruru init")
        sys.exit(1)

    cmd_arg = sys.argv[1]

    if cmd_arg == "history":
        if len(sys.argv) > 2:
            if sys.argv[2] == "--clear":
                show_history(clear=True)
            elif sys.argv[2] == "--last" and len(sys.argv) > 3:
                try:
                    n = int(sys.argv[3])
                    show_history(last=n)
                except ValueError:
                    print("Invalid number for --last")
            else:
                show_history()
        else:
            show_history()
    elif cmd_arg == "undo":
        undo()
    elif cmd_arg == "switch":
        switch_backend()
    elif cmd_arg == "explain":
        if len(sys.argv) < 3:
            print("Usage: ruru explain <command>")
            sys.exit(1)
        cmd = " ".join(sys.argv[2:])
        explanation = explain_command(cmd)
        if explanation:
            print(explanation)
    elif cmd_arg == "init":
        init_config()
    else:
        # Check for --dry
        if len(sys.argv) > 2 and sys.argv[-1] == "--dry":
            task = " ".join(sys.argv[1:-1])
            run_flow(task, dry=True)
        else:
            task = " ".join(sys.argv[1:])
            run_flow(task)
