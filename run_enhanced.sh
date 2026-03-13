#!/bin/bash
# Quick Setup and Launch Script for Enhanced App

echo "=================================================="
echo "⚖️  Legal Document AI Chat - Enhanced Edition"
echo "=================================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create it first: python -m venv venv"
    exit 1
fi

# Activate venv
echo "📦 Activating virtual environment..."
source venv/Scripts/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo ""
    echo "You have 3 options:"
    echo "1. Interactive setup: python setup_gemini_interactive.py"
    echo "2. Manual: Create .env with your Gemini API key"
    echo "3. Run without Gemini (basic mode): streamlit run app_enhanced.py"
    echo ""
    read -p "Do you have a Gemini API key? (yes/no): " has_key

    if [ "$has_key" = "yes" ]; then
        python setup_gemini_interactive.py
    else
        echo ""
        echo "Get your free API key: https://aistudio.google.com/app/apikeys"
        echo "Then run setup again: python setup_gemini_interactive.py"
        echo ""
    fi
else
    echo "✅ .env file found - API key configured"
fi

echo ""
echo "=================================================="
echo "🚀 Starting Enhanced App..."
echo "=================================================="
echo ""
echo "Opening: http://localhost:8501"
echo ""
echo "To stop: Press Ctrl+C"
echo ""

# Launch app
streamlit run app_enhanced.py
