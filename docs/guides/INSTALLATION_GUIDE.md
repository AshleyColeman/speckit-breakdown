# SpecKit Breakdown - Installation Guide

## ✅ Successfully Published!

**Repository**: https://github.com/AshleyColeman/speckit-breakdown

---

## 🚀 Quick Install (For Anyone)

### Interactive Installation

```bash
# Navigate to your project
cd /path/to/your/project

# Download and run the interactive installer
curl -fsSL https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/install.sh -o /tmp/sb-install.sh
chmod +x /tmp/sb-install.sh
/tmp/sb-install.sh
rm /tmp/sb-install.sh
```

**One-liner:**
```bash
curl -fsSL https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/install.sh -o /tmp/sb-install.sh && chmod +x /tmp/sb-install.sh && /tmp/sb-install.sh && rm /tmp/sb-install.sh
```

The installer will show you a menu to select your IDE (Windsurf, Cursor, VS Code, or Other).

---

## 📋 What Was Installed

```
your-project/
├── .windsurf/
│   └── workflows/
│       └── speckit.breakdown.md  ← Added by installer
└── docs/
    └── features/                 ← Created by installer
```

---

## 🎯 How to Use It

### Step 1: Create Your Project Spec

Create `docs/PROJECT_SPEC.md`:

```markdown
# My Project Name

## Overview
What you're building and why

## Business Objectives
- Objective 1
- Objective 2

## Target Users
- User type 1: Description
- User type 2: Description

## Features & Requirements
- Feature 1: Detailed description
- Feature 2: Detailed description
- Feature 3: Detailed description

## Technical Stack
- Framework: Next.js / React / etc.
- Database: PostgreSQL / MongoDB / etc.

## Timeline
- Duration: 3 months
- Team: 2 developers
```

### Step 2: Run the Breakdown

```bash
/speckit.breakdown docs/PROJECT_SPEC.md
```

### Step 3: Review Generated Files

```bash
# View master breakdown
cat docs/project-breakdown.md

# List all features
ls docs/features/
```

### Step 4: Process Each Feature with SpecKit

```bash
# For each feature:
/speckit.specify [feature description from feature-01-*.md]
/speckit.clarify
/speckit.plan
/speckit.tasks
/speckit.implement
```

---

## 📦 What You Get

After running `/speckit.breakdown`, you'll have:

### Master Breakdown Document
`docs/project-breakdown.md` containing:
- Feature summary table
- Implementation roadmap (MVP → Phase 2 → Phase 3)
- Dependency graph
- Timeline estimates

### Individual Feature Files
`docs/features/feature-[ID]-description.md` for each feature:
- Feature description
- User stories (3-6 per feature)
- Success criteria
- Scope (includes/excludes)
- Dependencies
- Ready-to-use `/speckit.specify` command

### Quick Start Script
`docs/features/quick-start.sh`:
- All commands in dependency order
- Copy-paste ready

---

## 🎯 Example Output

### Input: Simple E-commerce Spec
```markdown
# E-commerce Store

## Features
- Product catalog with categories
- Shopping cart and checkout
- User accounts with order history
- Payment via Stripe
- Admin dashboard
- Email notifications

## Tech: Next.js 14, PostgreSQL
## Timeline: 2 months, 1 developer
```

### Output: Generated Breakdown
```
✅ 6 Features Identified

F01: User Authentication (P1, 1.5 weeks)
F02: Product Catalog Browser (P1, 2 weeks)
F03: Shopping Cart & Checkout (P1, 2.5 weeks)
F04: Payment Integration (P1, 1.5 weeks)
F05: Admin Dashboard (P2, 2.5 weeks)
F06: Email Notifications (P3, 1 week)

MVP: F01-F04 (7.5 weeks)
Full Project: 11 weeks

Files created:
✅ docs/project-breakdown.md
✅ docs/features/feature-01-authentication.md
✅ docs/features/feature-02-product-catalog.md
✅ ... and 4 more
```

---

## 📚 Complete Example

See the **Next.js Admin Panel** example in the repo:
- https://github.com/AshleyColeman/speckit-breakdown/tree/main/examples/nextjs-admin-panel

This shows:
- Original 1,142-line spec
- Generated breakdown (12 features)
- All individual feature files
- Complete implementation roadmap

---

## 🔄 Workflow Integration

SpecKit Breakdown fits perfectly into the SpecKit workflow:

```
1. /speckit.breakdown     → Break project into features
   ↓
2. /speckit.specify       → Create detailed spec for each feature
   ↓
3. /speckit.clarify       → Resolve ambiguities
   ↓
4. /speckit.plan          → Generate implementation plan
   ↓
5. /speckit.tasks         → Create task breakdown
   ↓
6. /speckit.implement     → Execute implementation
```

---

## 💡 Tips for Best Results

### ✅ DO:
- Provide detailed feature descriptions in your spec
- Include user personas and their needs
- Specify technical constraints clearly
- Set realistic timelines

### ❌ DON'T:
- Be too vague ("user stuff", "products")
- Skip user stories
- Ignore dependencies
- Estimate without constraints

---

## 🆘 Troubleshooting

### Issue: "No features identified"
**Solution**: Add more detail to your project spec. Include specific workflows and requirements.

### Issue: ".windsurf/workflows not found"
**Solution**: Install SpecKit first, then run this installer.

### Issue: "Features too large"
**Solution**: The tool will automatically suggest splitting. Review and approve.

---

## 📖 Documentation

- **README**: https://github.com/AshleyColeman/speckit-breakdown/blob/main/README.md
- **Quick Start**: https://github.com/AshleyColeman/speckit-breakdown/blob/main/docs/guides/QUICK_START.md
- **Examples**: https://github.com/AshleyColeman/speckit-breakdown/tree/main/examples

---

## 🎉 You're Ready!

Install it in your project:

```bash
curl -fsSL https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/install.sh | bash
```

Then create your spec and run:

```bash
/speckit.breakdown docs/PROJECT_SPEC.md
```

Happy building! 🚀
