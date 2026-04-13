import os
import subprocess
import sys
import time  # New import for the delay
import json

def setup():
    print("🛠️ Profiler: Initializing Ruru-CLI...")

    # 1. Create the requested log directory
    log_path = os.path.expanduser("~/ruru1901/logs")
    os.makedirs(log_path, exist_ok=True)

    # 2. Create config directory and file
    config_dir = os.path.expanduser("~/.ruru")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.json")

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

    print(f"📂 Created log directory at {log_path}")
    print(f"📄 Created config at {config_path}")
    print("✅ System mapping complete.")
    print("\n💥 Task complete. Profiler is now self-destructing and clearing the screen in 5 seconds...")

    # 3. Self-destruction (Delete the file)
    try:
        if os.path.exists(__file__):
            os.remove(__file__)
    except Exception:
        pass
    time.sleep(5)
    os.system('clear' if os.name == 'posix' else 'cls')

if __name__ == "__main__":
    setup()
