#!/bin/bash

echo "🧠 Starting MBTI Personality Test Setup..."

# Check if .env exists, if not, create it from example
if [ ! -f ".env" ]; then
    echo "⚠️ No .env file found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it to add your OpenAI API key."
        echo "📝 Edit the .env file now? (y/n)"
        read edit_env
        if [[ $edit_env == "y" || $edit_env == "Y" ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        echo "❌ No .env.example file found. Creating basic .env file..."
        echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
        echo "FLASK_APP=app.py" >> .env
        echo "FLASK_ENV=development" >> .env
        echo "✅ Created basic .env file. Please edit it to add your OpenAI API key."
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check for OpenAI API key
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️ OpenAI API key not set in .env file."
    echo "📝 Please enter your OpenAI API key (or press Enter to skip):"
    read api_key
    if [ ! -z "$api_key" ]; then
        # Replace the placeholder with the actual API key
        sed -i "s/your_openai_api_key_here/$api_key/" .env
        echo "✅ API key updated."
    else
        echo "⚠️ No API key provided. You'll need to edit the .env file manually."
    fi
fi

# Run the application
echo "🚀 Starting the MBTI Personality Test application..."
python app.py 