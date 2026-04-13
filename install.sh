#!/bin/bash
# 1. Fix permissions immediately
chmod +x ruru.py profiler.py brain.py

# 2. Install dependencies
pip install groq requests --break-system-packages

# 3. Run the self-deleting profiler
python3 profiler.py

# 4. Create Alias (History and Historia both work)
SCRIPT_PATH=$(pwd)/ruru.py
ALIAS_LINE="alias ruru='python3 $SCRIPT_PATH'"
if ! grep -q "alias ruru=" ~/.bashrc; then
    echo "$ALIAS_LINE" >> ~/.bashrc
fi

echo "✅ Setup Complete. Run 'source ~/.bashrc' to begin."
