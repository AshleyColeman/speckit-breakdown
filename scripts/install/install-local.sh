#!/bin/bash
# SpecKit Breakdown Local Installer
# Use this to install from your local copy (before pushing to GitHub)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../" && pwd)"

echo "🚀 SpecKit Breakdown Local Installer"
echo "====================================="
echo "Installing from: $SCRIPT_DIR"
echo ""

# Get target directory from argument or current directory
TARGET_DIR="${1:-.}"
cd "$TARGET_DIR"

echo "Installing to: $(pwd)"
echo ""

# Check if we're in a project root
if [ ! -d ".git" ] && [ ! -f "package.json" ] && [ ! -f "pyproject.toml" ]; then
    echo "⚠️  Warning: This doesn't look like a project root directory."
    echo "   Current directory: $(pwd)"
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
    echo "Please install SpecKit first, then run this installer again."
    echo ""
    exit 1
fi

echo "✅ Found .windsurf/workflows directory"
echo ""

# Create docs/features directory if it doesn't exist
echo "📁 Creating docs/features directory..."
mkdir -p docs/features

# Copy the workflow file
WORKFLOW_FILE=".windsurf/workflows/speckit.breakdown.md"

echo "📝 Installing speckit.breakdown workflow..."
cp "$SCRIPT_DIR/workflows/speckit.breakdown.md" "$WORKFLOW_FILE"

# Make it readable
chmod +r "$WORKFLOW_FILE"

echo ""
echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 What was installed:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ .windsurf/workflows/speckit.breakdown.md"
echo "✅ docs/features/ (directory created)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Create your project specification:"
echo "   - Create a file like docs/PROJECT_SPEC.md"
echo "   - Use the template: $SCRIPT_DIR/templates/project-spec.template.md"
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
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Template: $SCRIPT_DIR/templates/project-spec.template.md"
echo "📖 Docs: $SCRIPT_DIR/README.md"
echo "🎯 Examples: $SCRIPT_DIR/examples/"
echo ""
echo "Happy building! 🎉"
