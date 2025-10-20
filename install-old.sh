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

# Detect IDE or ask user
IDE_TYPE=""

if [ -d ".windsurf" ]; then
    IDE_TYPE="windsurf"
    echo "✅ Detected: Windsurf IDE"
elif [ -f ".cursorrules" ] || [ -d ".cursor" ]; then
    IDE_TYPE="cursor"
    echo "✅ Detected: Cursor IDE"
else
    echo "🤔 Could not auto-detect IDE"
    echo ""
    echo "Which IDE are you using?"
    echo "1) Windsurf"
    echo "2) Cursor"
    echo "3) VS Code (with Cascade/Cline)"
    echo "4) Other"
    echo ""
    read -p "Enter choice (1-4): " -n 1 -r IDE_CHOICE
    echo ""
    
    case $IDE_CHOICE in
        1) IDE_TYPE="windsurf" ;;
        2) IDE_TYPE="cursor" ;;
        3) IDE_TYPE="vscode" ;;
        4) IDE_TYPE="other" ;;
        *) echo "Invalid choice. Defaulting to Windsurf."; IDE_TYPE="windsurf" ;;
    esac
fi

echo ""
echo "Installing for: $IDE_TYPE"
echo ""

# Create appropriate directories based on IDE
if [ "$IDE_TYPE" = "windsurf" ]; then
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
else
    # For Cursor/VS Code, create .windsurf/workflows if it doesn't exist
    mkdir -p .windsurf/workflows
    echo "✅ Created .windsurf/workflows directory"
fi

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
    curl -fsSL "https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/workflows/speckit.breakdown.md" -o "$WORKFLOW_FILE"
fi

# Make it executable (not needed for .md, but good practice)
chmod +r "$WORKFLOW_FILE"

# Create IDE-specific integration files
if [ "$IDE_TYPE" = "cursor" ] || [ "$IDE_TYPE" = "vscode" ]; then
    echo ""
    echo "📝 Creating IDE integration file..."
    
    cat > .cursorrules << 'EOF'
# SpecKit Breakdown - AI Assistant Integration

## Available Workflow

When the user requests to run the SpecKit breakdown workflow, follow these steps:

1. Read the workflow definition from: `.windsurf/workflows/speckit.breakdown.md`
2. Execute the workflow steps as defined
3. Create all required output files

## User Commands

The user can trigger this workflow by saying:
- "Run speckit breakdown on [file_path]"
- "Break down my project spec at [file_path]"
- "Execute /speckit.breakdown [file_path]"
- "Use the breakdown workflow on [file_path]"

## Workflow Location

`.windsurf/workflows/speckit.breakdown.md`

## Output Location

- Master breakdown: `docs/project-breakdown.md`
- Feature files: `docs/features/feature-[ID]-*.md`
- Quick start: `docs/features/quick-start.sh`

## Important

Always read and follow the complete workflow from the `.windsurf/workflows/speckit.breakdown.md` file.
Do not skip steps or improvise - follow the workflow exactly as written.
EOF
    
    echo "✅ Created .cursorrules integration file"
fi

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

if [ "$IDE_TYPE" = "windsurf" ]; then
    echo "2. Run the breakdown (Windsurf):"
    echo "   /speckit.breakdown docs/PROJECT_SPEC.md"
    echo ""
    echo "   Note: Reload Windsurf window (Ctrl+Shift+P → Reload Window)"
    echo "   if you don't see the /speckit.breakdown command"
elif [ "$IDE_TYPE" = "cursor" ] || [ "$IDE_TYPE" = "vscode" ]; then
    echo "2. Run the breakdown (Cursor/VS Code):"
    echo "   Tell your AI assistant:"
    echo "   'Run speckit breakdown on docs/PROJECT_SPEC.md'"
    echo ""
    echo "   Or:"
    echo "   'Execute the breakdown workflow on docs/PROJECT_SPEC.md'"
else
    echo "2. Run the breakdown:"
    echo "   Tell your AI assistant:"
    echo "   'Run speckit breakdown on docs/PROJECT_SPEC.md'"
fi

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
