# 🚀 Ruru-CLI
An expert AI assistant for your terminal.

## 1. Prerequisites
You must have Python 3 and the Gemini CLI installed:

TO INSTALL GEMINI
#refer gemini-cli installation
=>pip install gemini-cli --break-system-packages`
=>gemini auth login

## 2. Installation
IN TERMINAL
=>git clone [https://github.com/ruru1901/ruru-cli.git](https://github.com/ruru1901/ruru-cli.git)
=>cd ruru-cli
=>chmod +x install.sh
=>./install.sh
=>source ~/.bashrc

## 3.Usage

Commands

 ruru install <package> - Install software with AI risk assessment.

 ruru history - Access the interactive log menu.


 What is Ruru-CLI?

Ruru-CLI is a "Security-First" AI wrapper for the Linux command line. It acts as an intelligent intermediary between a user's intent (e.g., "I want to install software") and the actual execution of system-level commands.

Unlike a standard shell that executes commands blindly, Ruru-CLI uses a "Brain-and-Hand" architecture to ensure the user understands the risks and the function of every command before it touches the system.
How It Works: The Architecture

Ruru-CLI operates through three distinct phases: the Profiler, the Brain, and the Hand.
1. The Setup (The Profiler)

When first installed, a script called profiler.py runs to prepare the environment.

    Environment Mapping: It creates a dedicated directory structure (~/ruru1901/logs) to ensure all actions are audited.

    Self-Destruction: To keep the system clean, the profiler deletes its own source code after execution, leaving only the main application behind.

    Alias Integration: It injects a shortcut into the user's .bashrc file, allowing the user to simply type ruru from any directory.

2. The Intelligence (The Brain)

When you type a command like ruru install nmap, the "Brain" (powered by Gemini AI) is activated.

    Structured Analysis: Instead of just running the command, Ruru sends the task to the AI to generate a risk assessment.

    The Template: The AI is forced to respond using a specific template:

        Task Name: What is being done.

        Command: The exact syntax to be used.

        Function: A human-readable explanation of the command's purpose.

        Risk Level: A categorization (Low, Mid, or High).

        Why?: A technical justification for the risk level.

3. The Execution (The Hand)

Once the user reviews the AI's proposal and types y (Yes), the "Hand" takes over.

    Hidden Execution: Ruru executes the command in a background subprocess. This keeps the terminal clean by hiding messy installation logs or progress bars.

    Visual Feedback: To let the user know the system hasn't frozen, a "Thinking" and "Working" spinner animation is displayed.

    Sudo Management: It intelligently handles sudo prompts by requesting privileges before starting the background process, preventing the system from hanging on a hidden password request.

    Cache Refresh: After a successful installation, it runs hash -r to ensure the new software is immediately available in the current session.

Key Features
🛠️ Self-Healing Dependencies

Ruru-CLI includes logic to detect if necessary Python libraries (like google-generativeai) are missing. On modern systems like Ubuntu 24.04 (Python 3.12+), it automatically bypasses environment restrictions using the --break-system-packages flag to ensure the tool stays functional.
📜 Menu-Driven History

Instead of a simple text file, Ruru-CLI features an interactive, menu-driven archive. By typing ruru history, users can:

    View a chronological log of every AI-approved task.

    Search for specific commands by keyword.

    Clear logs to maintain privacy.

🔒 Security-First Design

By requiring a manual "Accept" step after an AI explanation, Ruru-CLI prevents "copy-paste" errors where users might run dangerous commands found online without understanding what they do.
The User Workflow

    Request: User types ruru install <package>.

    Analyze: Ruru Brain displays a structured risk report.

    Approve: User reviews and accepts the proposal.

    Deploy: Ruru Hand installs the software silently with a loading spinner.

    Audit: The action is saved to the ruru1901 logs for future reference.


Ruru-CLI: The AI Bridge to Linux Mastery

Ruru-CLI is a specialized command-line companion designed to turn the intimidating Linux terminal into a transparent, educational, and safe environment. It acts as a "Guardian" that sits between you and the operating system, explaining exactly what is happening before any changes are made.
What does it do?

Ruru-CLI replaces the "blind execution" of commands with a Review-and-Execute workflow.

    Translates Code to English: It takes a complex command like sudo apt-get install -y nmap and explains it in a simple paragraph so you know exactly what the "flags" (like -y) are doing.

    Assesses Danger: It uses an AI Brain to label tasks as Low, Mid, or High Risk, preventing beginners from accidentally running commands that could delete data or break the system.

    Silent Execution: It hides the "scary" walls of text that usually fly by during an installation, replacing them with a clean loading spinner.

    Automatic Auditing: It keeps a searchable history of everything you've done in a dedicated folder (~/ruru1901/logs), making it easy to track your progress.

Who can use it?

    Windows/Mac Migrants: People who are used to "Installers" and "App Stores" and find the empty Linux terminal confusing.

    Cybersecurity Students: Those who need tools like nmap or metasploit but want to understand the dependencies being installed.

    Developers: Anyone who wants a clean, logged history of their system configuration without cluttering their terminal screen.

Why it's a "Game-Changer" for Beginners

Moving to Linux is often hard because of the "Copy-Paste Culture." Beginners often copy commands from the internet without knowing what they do.

Ruru-CLI solves this by:

    Building Confidence: By reading the "Function" and "Why?" sections for every command, a beginner naturally starts learning Linux syntax.

    Reducing "Terminal Anxiety": The hidden background execution makes the terminal feel more like a modern app and less like an 80s computer screen.

    Safety Net: The requirement to type y after seeing a "High Risk" warning forces a moment of reflection, saving users from common "newbie" mistakes.
