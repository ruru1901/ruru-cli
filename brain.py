import os
import json
import sys

# For Groq
try:
    import groq
except ImportError:
    groq = None

# For OpenRouter
try:
    import requests
except ImportError:
    requests = None

def analyze_task(user_task: str) -> dict:
    config_path = os.path.expanduser("~/.ruru/config.json")
    if not os.path.exists(config_path):
        print("❌ Config file not found. Run profiler.py first.")
        sys.exit(1)

    with open(config_path, 'r') as f:
        config = json.load(f)

    backend = config.get("ai_backend", "groq")
    prompt = f"Expert Linux CLI. Task: '{user_task}'. Provide ONLY a JSON response with the following keys: command (the Linux command to execute), risk (Low, Mid, or High), explanation (brief description of what the command does), warning (any risks or precautions)."

    if backend == "groq":
        if groq is None:
            print("❌ groq package not installed. Run 'pip install groq'")
            sys.exit(1)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY environment variable not set. Set it with 'export GROQ_API_KEY=your_key'")
            sys.exit(1)
        model = config.get("groq_model", "llama3-70b-8192")
        client = groq.Groq(api_key=api_key)
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                timeout=15
            )
            response_text = chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return None

    elif backend == "openrouter":
        if requests is None:
            print("❌ requests package not installed. Run 'pip install requests'")
            sys.exit(1)
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("❌ OPENROUTER_API_KEY environment variable not set. Set it with 'export OPENROUTER_API_KEY=your_key'")
            sys.exit(1)
        model = config.get("openrouter_model", "meta-llama/llama-3-70b-instruct")
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "ruru-cli",
            "X-Title": "ruru-cli",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=15)
            response.raise_for_status()
            response_text = response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"❌ OpenRouter API error: {e}")
            return None

    else:
        print("❌ Invalid backend in config.")
        return None

    # Strip markdown fences if present
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:].strip()

    try:
        result = json.loads(response_text)
        return result
    except json.JSONDecodeError:
        print("❌ Invalid JSON response from AI.")
        return None

def explain_command(command: str) -> str:
    config_path = os.path.expanduser("~/.ruru/config.json")
    if not os.path.exists(config_path):
        print("❌ Config file not found. Run profiler.py first.")
        sys.exit(1)

    with open(config_path, 'r') as f:
        config = json.load(f)

    backend = config.get("ai_backend", "groq")
    prompt = f"Explain this Linux command in plain English for a beginner: '{command}'. Break it into: 1) What it does, 2) What each flag or argument means, 3) Any risks or side effects. Be concise and clear."

    if backend == "groq":
        if groq is None:
            print("❌ groq package not installed.")
            return None
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY not set.")
            return None
        model = config.get("groq_model", "llama3-70b-8192")
        client = groq.Groq(api_key=api_key)
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                timeout=15
            )
            response_text = chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return None

    elif backend == "openrouter":
        if requests is None:
            print("❌ requests package not installed.")
            return None
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("❌ OPENROUTER_API_KEY not set.")
            return None
        model = config.get("openrouter_model", "meta-llama/llama-3-70b-instruct")
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "ruru-cli",
            "X-Title": "ruru-cli",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=15)
            response.raise_for_status()
            response_text = response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"❌ OpenRouter API error: {e}")
            return None

    else:
        print("❌ Invalid backend.")
        return None

    # Strip markdown if present
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith(""):
            response_text = response_text[5:].strip()

    return response_text