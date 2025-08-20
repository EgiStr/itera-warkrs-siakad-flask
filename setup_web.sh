#!/bin/bash
# WAR KRS Web Application Setup Script

echo "🚀 WAR KRS Web Application Setup"
echo "================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 is available"

# Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Use pip3 if available, otherwise pip
PIP_CMD="pip"
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
fi

echo "✅ pip is available"

# Install dependencies
echo "📦 Installing Flask dependencies..."
$PIP_CMD install Flask==2.2.5 Flask-Login==0.6.2 Flask-WTF==1.1.1 Flask-Bcrypt==1.0.1 Flask-SQLAlchemy==3.0.5 WTForms==3.0.1 Werkzeug==2.2.3 cryptography==41.0.7

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    echo "🔧 Try installing manually:"
    echo "   pip install -r requirements-flask.txt"
    exit 1
fi

# Install existing project dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing existing project dependencies..."
    $PIP_CMD install -r requirements.txt
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "🚀 To start the web application:"
echo "   python3 start_web.py"
echo ""
echo "📍 The application will be available at:"
echo "   http://localhost:5000"
echo ""
echo "📋 Next steps:"
echo "1. Run: python3 start_web.py"
echo "2. Open browser to http://localhost:5000"
echo "3. Register a new account"
echo "4. Configure SIAKAD credentials in Settings"
echo "5. Select target courses"
echo "6. Start WAR process from Dashboard"
