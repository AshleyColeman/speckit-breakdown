# How to Set Up SpecKit Breakdown as a GitHub Repo

## Overview

SpecKit Breakdown is an **enhancement** to the official SpecKit system. Users must install SpecKit first, then add this breakdown capability.

## User Installation Flow (Two-Step Process)

### Step 1: Install Official SpecKit (Required)
```bash
# Install the official SpecKit CLI
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Initialize SpecKit in their project
specify init . --ai claude  # or their preferred AI

# Verify installation
specify check
```

### Step 2: Install SpecKit Breakdown (Your Enhancement)
```bash
# From within their project (after Step 1)
curl -fsSL https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/install.sh | bash
```

## Quick Setup (5 minutes)

### Step 1: Create GitHub Repository

```bash
# On GitHub.com:
# 1. Click "New Repository"
# 2. Name: "speckit-breakdown"
# 3. Description: "Transform complete projects into SpecKit-ready features"
# 4. Public or Private (your choice)
# 5. Don't initialize with README (we already have one)
# 6. Create repository
```

### Step 2: Initialize and Push

```bash
# Navigate to the speckit-breakdown directory
cd /tmp/speckit-breakdown

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: SpecKit Breakdown v1.0.0"

# Add your GitHub repo as remote (replace with your username)
git remote add origin https://github.com/AshleyColeman/speckit-breakdown.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Update Documentation to Reference Two-Step Installation

Update your README.md and other documentation to clearly state the two-step installation process:

1. **Original SpecKit installation first** (official GitHub repo)
2. **Your enhancement second** (your GitHub repo)

Example for your README.md:
```markdown
## Installation

### Step 1: Install Official SpecKit (Required First)
[Instructions to install from github/spec-kit]

### Step 2: Install SpecKit Breakdown (Enhancement)
[Instructions to install from your repo]
```

### Step 4: Test the Installer

```bash
# Go to any test project
cd /path/to/test/project

# Run your installer
curl -fsSL https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/install.sh | bash
```

### Step 5: Update install.sh URLs

Edit `install.sh` and replace `YOUR_USERNAME` with your actual GitHub username:

```bash
# Line 42: Update this URL
curl -fsSL "https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/workflows/speckit.breakdown.md" -o "$WORKFLOW_FILE"
```

Then commit and push:

```bash
git add install.sh
git commit -m "Update installer with correct GitHub username"
git push
```

---

## Making It Easy to Install

### Option 1: One-Line Install (Recommended)

Users run:
```bash
curl -fsSL https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/install.sh | bash
```

### Option 2: Copy-Paste Install

Add to README:
```bash
# Create workflow directory if needed
mkdir -p .windsurf/workflows

# Download the workflow
curl -O https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/workflows/speckit.breakdown.md

# Move to workflows
mv speckit.breakdown.md .windsurf/workflows/

# Create features directory
mkdir -p docs/features
```

### Option 3: Git Submodule (Advanced)

For users who want to track updates:
```bash
git submodule add https://github.com/AshleyColeman/speckit-breakdown.git .speckit-breakdown
ln -s .speckit-breakdown/workflows/speckit.breakdown.md .windsurf/workflows/
```

---

## Installation Flow

```
User's Project
├── .windsurf/
│   └── workflows/
│       ├── speckit.specify.md      (from SpecKit)
│       ├── speckit.plan.md         (from SpecKit)
│       └── speckit.breakdown.md    (← Your tool adds this)
└── docs/
    └── features/                   (← Your tool creates this)
```

---

## Update Process

### When you improve the tool:

```bash
# Make changes
vi workflows/speckit.breakdown.md

# Update version
echo "1.0.1" > VERSION

# Commit
git add .
git commit -m "v1.0.1: Improved feature sizing logic"
git tag v1.0.1
git push origin main --tags
```

### Users update with:

```bash
# Re-run installer to get latest
curl -fsSL https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/install.sh | bash
```

---

## Recommended Repository Structure

```
speckit-breakdown/
├── README.md                      # Main documentation
├── docs/guides/QUICK_START.md     # 5-minute guide
├── docs/maintainers/SETUP_AS_REPO.md   # This file
├── VERSION                        # Version tracking
├── LICENSE                        # MIT recommended
├── install.sh                     # One-command installer
├── scripts/install/install-local.sh  # Local installer
├── workflows/
│   └── speckit.breakdown.md      # The workflow file
├── templates/
│   ├── project-spec.template.md  # Template for users
│   └── feature.template.md       # Feature file template
├── examples/
│   ├── ecommerce/                # Example breakdown
│   ├── saas-dashboard/           # Example breakdown
│   └── admin-panel/              # Example breakdown (you have this!)
└── .github/
    └── workflows/
        └── test.yml              # CI/CD (optional)
```

---

## Add Your Admin Panel as Example

```bash
# Create examples directory
mkdir -p examples/admin-panel

# Copy your breakdown
cp /home/ashleycoleman/Projects/product_scraper/docs/nextjs-admin-project-breakdown.md \
   examples/admin-panel/

# Copy feature files
cp -r /home/ashleycoleman/Projects/product_scraper/docs/features/ \
   examples/admin-panel/

# Commit
git add examples/
git commit -m "Add Next.js Admin Panel example"
git push
```

---

## Optional: Add to Package Managers

### npm (if you want)

Create `package.json`:
```json
{
  "name": "@AshleyColeman/speckit-breakdown",
  "version": "1.0.0",
  "description": "Transform projects into SpecKit-ready features",
  "bin": {
    "speckit-breakdown": "./install.sh"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/AshleyColeman/speckit-breakdown"
  },
  "keywords": ["speckit", "project-planning", "windsurf"],
  "author": "Your Name",
  "license": "MIT"
}
```

Then users can:
```bash
npx @AshleyColeman/speckit-breakdown
```

---

## Make It Discoverable

### Add to README.md badges:

```markdown
[![Install](https://img.shields.io/badge/install-one--command-blue)]()
[![Version](https://img.shields.io/badge/version-1.0.0-green)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
```

### Add topics to GitHub repo:
- speckit
- windsurf
- cascade-ai
- project-planning
- feature-breakdown
- workflow-automation

---

## Testing Checklist

Before publishing:

- [ ] README is clear and complete
- [ ] install.sh works on fresh project
- [ ] All URLs updated with your GitHub username
- [ ] Examples directory has at least one example
- [ ] VERSION file is correct
- [ ] LICENSE file added (MIT recommended)
- [ ] Tested on macOS/Linux
- [ ] Quick start guide is accurate

---

## Share It!

Once published, share:

1. **GitHub Discussions**: Announce in SpecKit community
2. **Twitter/X**: Tweet about your tool
3. **Dev.to**: Write a blog post
4. **Reddit**: Share in r/programming or relevant subs
5. **Discord**: Share in Windsurf/Cascade communities

Example tweet:
```
🚀 Just released SpecKit Breakdown - transform your project specs 
into perfectly-sized features ready for @SpecKit processing!

One command install. Works with any project.

https://github.com/YOUR_USERNAME/speckit-breakdown

#SpecKit #Windsurf #CascadeAI
```

---

## That's It!

Your tool is now:
✅ Versioned on GitHub
✅ Easy to install (one command)
✅ Easy to update
✅ Shareable with community
✅ Documented with examples

**Ready to publish!** 🎉
