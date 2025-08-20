#!/bin/bash

# WAR KRS Flask - Vercel Deployment Preparation Script

echo "🚀 Preparing WAR KRS Flask for Vercel deployment..."
echo "=================================================="

# Check if required files exist
echo "📁 Checking required files..."

required_files=(
    "vercel.json"
    "api/index.py"
    "requirements.txt"
    "Pipfile"
    "app.py"
    "config_flask.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo "❌ Missing required files:"
    printf '   %s\n' "${missing_files[@]}"
    exit 1
fi

echo "✅ All required files present"

# Generate keys if not exists
echo ""
echo "🔐 Generating environment keys..."
python generate_keys.py > deployment_keys.txt
echo "✅ Keys saved to deployment_keys.txt"

# Test basic import
echo ""
echo "🧪 Testing Python imports..."
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from app import app
    print('✅ Flask app import successful')
except Exception as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"

echo ""
echo "📋 Deployment checklist:"
echo "========================"
echo "✅ 1. Files prepared for Vercel"
echo "✅ 2. Environment keys generated"
echo "✅ 3. Python imports tested"
echo ""
echo "🔄 Next steps:"
echo "1. Create/setup your Vercel account"
echo "2. Set environment variables from deployment_keys.txt"
echo "3. Setup external database (recommended: Supabase PostgreSQL)"
echo "4. Push to GitHub and deploy via Vercel dashboard"
echo ""
echo "📚 Read VERCEL_DEPLOYMENT.md for detailed instructions"
echo ""
echo "Environment keys are in: deployment_keys.txt"
echo "⚠️  Don't commit deployment_keys.txt to git!"

# Add to .gitignore if not exists
if ! grep -q "deployment_keys.txt" .gitignore 2>/dev/null; then
    echo "deployment_keys.txt" >> .gitignore
    echo "✅ Added deployment_keys.txt to .gitignore"
fi

echo ""
echo "🎉 Ready for Vercel deployment!"
