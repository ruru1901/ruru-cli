import subprocess
import sys
import os
import shlex
import time
import itertools
from datetime import datetime

# --- CONFIG ---
LOG_DIR = os.path.expanduser("~/ruru1901/logs")
LOG_FILE = os.path.join(LOG_DIR, "history.log")

def ensure_logs():
    os.makedirs(LOG_DIR, exist_ok=True)

# --- THE BRAIN (Gemini CLI) ---
def ask_gemini(task, command):
    prompt = f"""
    You are an expert AI assistant for Linux config command-line tasks.
    For the task of '{task}', generate a response following this template exactly:

    Task Name: {task}
    Command:
    1 {command} # Main task command

    Function: Explain the overall purpose and outcome of this command sequence in a human-readable paragraph.
    Risk Level: [Low, Mid, or High]
    Why?: Brief direct explanation of risks.
    """
    try:
        output = subprocess.check_output(["gemini", prompt], stderr=subprocess.STDOUT, text=True)
        return output.strip()
    except Exception:
        return "⚠️ Brain Offline. Ensure gemini-cli is installed and 'gemini auth login' is done."

def spinning_cursor():
    return itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

# --- THE HAND (Hidden Terminal + Spinner) ---
def execute_hidden(command):
    if "sudo" in command:
        print("\n🔐 Ruru needs sudo privileges:")
        subprocess.run(["sudo", "-v"]) 

    spinner = spinning_cursor()
    print("\n🚀 RURU HAND: Executing task...")
    
    # We use a context manager to handle the process and capture errors
    try:
        # Start the process. stderr=subprocess.PIPE allows us to check for lock errors
        process = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )

        while process.poll() is None:
            sys.stdout.write(f"\r{next(spinner)} Working... ")
            sys.stdout.flush()
            time.sleep(0.1)
        
        # Check for errors in the background
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            sys.stdout.write("\r✅ Done! Installation successful.          \n")
            return "SUCCESS"
        else:
            sys.stdout.write("\r❌ Task Failed!                          \n")
            if "lock" in stderr.lower():
                print("⚠️ Error: The package manager is locked by another process.")
                print("Wait a moment or check if another update is running.")
            else:
                print(f"⚠️ Debug Info: {stderr.strip()}")
            return "FAILED"

    except Exception as e:
        print(f"\r❌ Error: {str(e)}")
        return "ERROR"

# --- MENU-DRIVEN HISTORY ---
def history_menu():
    ensure_logs()
    if not os.path.exists(LOG_FILE):
        print("Empty history.")
        return

    while True:
        print("\n📜 --- RURU HISTORY MENU ---")
        print("1. View All Logs")
        print("2. Clear History")
        print("3. Search for a Task")
        print("4. Exit Menu")
        
        choice = input("\nSelect an option: ")
        
        if choice == '1':
            with open(LOG_FILE, "r") as f:
                print("\n" + f.read())
        elif choice == '2':
            confirm = input("Are you sure? (y/n): ")
            if confirm == 'y':
                open(LOG_FILE, 'w').close()
                print("History cleared.")
        elif choice == '3':
            query = input("Enter keyword to search: ")
            with open(LOG_FILE, "r") as f:
                for line in f:
                    if query.lower() in line.lower():
                        print(line.strip())
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

def run_flow(task_name, full_cmd):
    analysis = ask_gemini(task_name, full_cmd)
    print("\n" + "="*60)
    print(analysis)
    print("="*60)
    
    if "Brain Offline" in analysis: return

    confirm = input("\nDo you accept this proposal? (y/n): ").lower()
    if confirm == 'y':
        status = execute_hidden(full_cmd)
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {task_name} | {status}\n")
    else:
        print("❌ Proposal rejected.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ruru install <pkg> | ruru historia")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "install" and len(sys.argv) > 2:
        pkg = sys.argv[2]
        run_flow(f"Install {pkg}", f"sudo apt-get install -y {pkg}")
    elif cmd in ["historia", "history"]:
        history_menu()
