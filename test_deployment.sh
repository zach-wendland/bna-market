#!/bin/bash
# Quick deployment readiness check

echo "🔍 Checking deployment configuration..."
echo ""

# Check required files exist
echo "✓ Checking required files..."
required_files=("Procfile" "requirements.txt" "runtime.txt" "render.yaml" "railway.json")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing"
        exit 1
    fi
done
echo ""

# Check Python version
echo "✓ Checking Python version..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo "  ✓ $python_version"
else
    echo "  ✗ Python 3 not found"
    exit 1
fi
echo ""

# Check gunicorn in requirements
echo "✓ Checking gunicorn dependency..."
if grep -q "gunicorn" requirements.txt; then
    echo "  ✓ gunicorn found in requirements.txt"
else
    echo "  ✗ gunicorn missing from requirements.txt"
    exit 1
fi
echo ""

# Validate Procfile syntax
echo "✓ Validating Procfile..."
if [ -s "Procfile" ]; then
    echo "  ✓ Procfile is not empty"
else
    echo "  ✗ Procfile is empty"
    exit 1
fi
echo ""

echo "✅ Deployment configuration looks good!"
echo ""
echo "Next steps:"
echo "1. Commit these changes: git add . && git commit -m 'Add Railway/Render deployment config'"
echo "2. Push to GitHub: git push origin main"
echo "3. Deploy to Railway or Render (see DEPLOYMENT.md)"
