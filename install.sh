#!/bin/bash
# SpecKit Breakdown Installer
# Installs the /speckit.breakdown workflow into your project

set -e

echo "🚀 SpecKit Breakdown Installer"
echo "================================"
echo ""

# Check if we're in a project root
if [ ! -d ".git" ] && [ ! -f "package.json" ] && [ ! -f "pyproject.toml" ]; then
    echo "⚠️  Warning: This doesn't look like a project root directory."
    echo "   Make sure you're in your project's root folder."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if SpecKit is installed
if [ ! -d ".windsurf/workflows" ]; then
    echo "❌ Error: .windsurf/workflows directory not found!"
    echo ""
    echo "Please install SpecKit first:"
    echo "1. Visit https://speckit.dev (or your SpecKit source)"
    echo "2. Follow their installation instructions"
    echo "3. Then run this installer again"
    echo ""
    exit 1
fi

echo "✅ Found .windsurf/workflows directory"
echo ""

# Create docs/features directory if it doesn't exist
echo "📁 Creating docs/features directory..."
mkdir -p docs/features

# Download or copy the workflow file
WORKFLOW_FILE=".windsurf/workflows/speckit.breakdown.md"

if [ -f "$(dirname "$0")/workflows/speckit.breakdown.md" ]; then
    # Local installation
    echo "📝 Installing speckit.breakdown workflow (local)..."
    cp "$(dirname "$0")/workflows/speckit.breakdown.md" "$WORKFLOW_FILE"
else
    # Remote installation
    echo "📝 Downloading speckit.breakdown workflow..."
    curl -fsSL "https://raw.githubusercontent.com/YOUR_USERNAME/speckit-breakdown/main/workflows/speckit.breakdown.md" -o "$WORKFLOW_FILE"
fi

# Make it executable (not needed for .md, but good practice)
chmod +r "$WORKFLOW_FILE"

echo ""
echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Create your project specification:"
echo "   - Create a file like docs/PROJECT_SPEC.md"
echo "   - Include: objectives, users, features, tech stack"
echo ""
echo "2. Run the breakdown:"
echo "   /speckit.breakdown docs/PROJECT_SPEC.md"
echo ""
echo "3. Review generated files:"
echo "   - docs/project-breakdown.md (master breakdown)"
echo "   - docs/features/feature-*.md (individual features)"
echo ""
echo "4. Process each feature with SpecKit:"
echo "   /speckit.specify [feature description]"
echo "   /speckit.clarify"
echo "   /speckit.plan"
echo "   /speckit.tasks"
echo "   /speckit.implement"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Documentation: See README.md for detailed usage"
echo "💡 Examples: Check examples/ directory for samples"
echo ""
echo "Happy building! 🎉"
