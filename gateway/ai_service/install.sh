#!/bin/bash
set -e  # Exit immediately on error

echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "⬆️ Ensuring spaCy 3.8.0 is installed..."
pip install spacy==3.8.0

echo "🧠 Downloading spaCy model: en_core_web_md"
python -m spacy download en_core_web_md

echo "✅ Setup complete. Activate the venv with 'source venv/bin/activate'"
