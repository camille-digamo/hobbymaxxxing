#!/bin/bash
# Railway Dependency Fix Script
# Run this if getting import errors on Railway

echo "🔧 FIXING RAILWAY DEPENDENCIES"
echo "==============================="

echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

echo "📦 Installing requirements with no cache..."
pip install --no-cache-dir --force-reinstall -r requirements.txt

echo "🧪 Testing dependencies..."
python check_dependencies.py

echo "✅ Dependency fix complete!"
echo "Railway should now work properly."