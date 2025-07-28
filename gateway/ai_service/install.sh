#!/bin/bash
set -e  # Exit on any error

echo "🔧 [1/6] Creating virtual environment..."
python3 -m venv venv

echo "🐍 [2/6] Activating virtual environment..."
source venv/bin/activate

echo "📦 [3/6] Upgrading pip..."
pip install --upgrade pip

echo "📚 [4/6] Installing Python dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found. Skipping."
fi

echo "🧠 [5/6] Installing spaCy 3.8.0 and downloading model..."
pip install spacy==3.8.0
python -m spacy download en_core_web_md

echo "✅ [6/6] Setup complete!"
echo "👉 Run: 'source venv/bin/activate' to activate the virtual environment."
