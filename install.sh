#!/bin/bash
# SpecKit Breakdown Interactive Installer
# Interactive menu-driven installation

set -e

SPECKIT_BREAKDOWN_REPO_DEFAULT="AshleyColeman/speckit-breakdown"
SPECKIT_BREAKDOWN_REF_DEFAULT="main"

SPECKIT_BREAKDOWN_REPO="${SPECKIT_BREAKDOWN_REPO:-$SPECKIT_BREAKDOWN_REPO_DEFAULT}"
SPECKIT_BREAKDOWN_REF="${SPECKIT_BREAKDOWN_REF:-$SPECKIT_BREAKDOWN_REF_DEFAULT}"

while [ "$#" -gt 0 ]; do
    case "$1" in
        --repo)
            SPECKIT_BREAKDOWN_REPO="$2"
            shift 2
            ;;
        --ref)
            SPECKIT_BREAKDOWN_REF="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Colors for better UX
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                            ║${NC}"
echo -e "${CYAN}║      ${GREEN}🚀 SpecKit Breakdown Installer${CYAN}      ║${NC}"
echo -e "${CYAN}║                                            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in a project root
if [ ! -d ".git" ] && [ ! -f "package.json" ] && [ ! -f "pyproject.toml" ]; then
    echo -e "${YELLOW}⚠️  Warning: This doesn't look like a project root directory.${NC}"
    echo "   Current directory: $(pwd)"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}Which IDE/Editor are you using?${NC}"
echo ""
echo "  1) 🌊 Windsurf (Native slash commands)"
echo "  2) 🖱️  Cursor (AI assistant integration)"
echo "  3) 💻 VS Code with Cascade/Cline"
echo "  4) 🤷 Other / Not sure"
echo ""
read -p "Enter your choice (1-4): " IDE_CHOICE

case $IDE_CHOICE in
    1)
        IDE_TYPE="windsurf"
        IDE_NAME="Windsurf"
        ;;
    2)
        IDE_TYPE="cursor"
        IDE_NAME="Cursor"
        ;;
    3)
        IDE_TYPE="vscode"
        IDE_NAME="VS Code"
        ;;
    4)
        IDE_TYPE="other"
        IDE_NAME="Other"
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Installing for: ${IDE_NAME}${NC}"
echo ""

# Create appropriate directories based on IDE
if [ "$IDE_TYPE" = "windsurf" ]; then
    if [ ! -d ".windsurf/workflows" ]; then
        echo -e "${YELLOW}⚠️  SpecKit not detected. Attempting to install...${NC}"
        
        # 1. Install CLI if missing
        if ! command -v specify &> /dev/null; then
            echo "Installing specify-cli..."
            if command -v uv &> /dev/null; then
                uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
            else
                echo -e "${RED}❌ Error: 'uv' is not installed.${NC} Please install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh"
                exit 1
            fi
        fi

        # 2. Initialize project
        echo "Initializing SpecKit project..."
        specify init

        # 3. Verify again
        if [ ! -d ".windsurf/workflows" ]; then
             echo -e "${RED}❌ Error: Failed to initialize SpecKit.${NC} .windsurf/workflows still missing."
             exit 1
        fi
        echo -e "${GREEN}✅ SpecKit installed and initialized${NC}"
    fi
    echo -e "${GREEN}✅ Found .windsurf/workflows directory${NC}"
else
    # For Cursor/VS Code, create .windsurf/workflows if it doesn't exist
    mkdir -p .windsurf/workflows
    echo -e "${GREEN}✅ Created .windsurf/workflows directory${NC}"
fi

# Create docs/features directory
echo -e "${BLUE}📁 Creating docs/features directory...${NC}"
mkdir -p docs/features

# Download the workflow file
WORKFLOW_FILE=".windsurf/workflows/speckit.breakdown.md"

echo -e "${BLUE}📝 Downloading speckit.breakdown workflow...${NC}"

if [ -f "$(dirname "$0")/workflows/speckit.breakdown.md" ]; then
    # Local installation
    cp "$(dirname "$0")/workflows/speckit.breakdown.md" "$WORKFLOW_FILE"
else
    # Remote installation
    echo -e "${CYAN}   Source: https://raw.githubusercontent.com/${SPECKIT_BREAKDOWN_REPO}/${SPECKIT_BREAKDOWN_REF}/workflows/speckit.breakdown.md${NC}"
    echo -e "${CYAN}   Tip: Pin to a release tag/commit with: SPECKIT_BREAKDOWN_REF=<tag-or-sha> ./install.sh${NC}"
    curl -fsSL "https://raw.githubusercontent.com/${SPECKIT_BREAKDOWN_REPO}/${SPECKIT_BREAKDOWN_REF}/workflows/speckit.breakdown.md" -o "$WORKFLOW_FILE"
fi

chmod +r "$WORKFLOW_FILE"

# Create IDE-specific integration files
if [ "$IDE_TYPE" = "cursor" ] || [ "$IDE_TYPE" = "vscode" ]; then
    echo ""
    echo -e "${BLUE}📝 Creating ${IDE_NAME} integration file...${NC}"
    
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
    
    echo -e "${GREEN}✅ Created .cursorrules integration file${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                            ║${NC}"
echo -e "${GREEN}║        ✅ Installation Complete! 🎉        ║${NC}"
echo -e "${GREEN}║                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}1. Create your project specification:${NC}"
echo "   - Create a file like docs/PROJECT_SPEC.md"
echo "   - Include: objectives, users, features, tech stack"
echo ""

if [ "$IDE_TYPE" = "windsurf" ]; then
    echo -e "${YELLOW}2. Run the breakdown (Windsurf):${NC}"
    echo "   /speckit.breakdown docs/PROJECT_SPEC.md"
    echo ""
    echo -e "${CYAN}   💡 Tip: Reload Windsurf window if you don't see the command${NC}"
    echo "      Press: Ctrl+Shift+P → 'Reload Window'"
elif [ "$IDE_TYPE" = "cursor" ] || [ "$IDE_TYPE" = "vscode" ]; then
    echo -e "${YELLOW}2. Run the breakdown (${IDE_NAME}):${NC}"
    echo "   Tell your AI assistant:"
    echo -e "   ${GREEN}'Run speckit breakdown on docs/PROJECT_SPEC.md'${NC}"
    echo ""
    echo "   Or:"
    echo -e "   ${GREEN}'Execute the breakdown workflow on docs/PROJECT_SPEC.md'${NC}"
else
    echo -e "${YELLOW}2. Run the breakdown:${NC}"
    echo "   Tell your AI assistant:"
    echo -e "   ${GREEN}'Run speckit breakdown on docs/PROJECT_SPEC.md'${NC}"
fi

echo ""
echo -e "${YELLOW}3. Review generated files:${NC}"
echo "   - docs/project-breakdown.md (master breakdown)"
echo "   - docs/features/feature-*.md (individual features)"
echo ""
echo -e "${YELLOW}4. Process each feature with SpecKit:${NC}"
echo "   /speckit.specify [feature description]"
echo "   /speckit.clarify"
echo "   /speckit.plan"
echo "   /speckit.tasks"
echo "   /speckit.implement"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📚 Documentation:${NC} https://github.com/AshleyColeman/speckit-breakdown"
echo -e "${BLUE}💡 Examples:${NC} Check examples/ directory for samples"
echo ""
echo -e "${GREEN}Happy building! 🚀${NC}"
echo ""
