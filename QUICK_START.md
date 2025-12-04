# Quick Start Guide - SpecKit Breakdown

## 5-Minute Setup

### Step 1: Install SpecKit (if not already installed)
```bash
# Visit https://speckit.dev and follow their instructions
# Or copy SpecKit workflows to .windsurf/workflows/
```

### Step 2: Install SpecKit Breakdown
```bash
cd /path/to/your/project

# Option A: Quick install from GitHub
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/speckit-breakdown/main/install.sh | bash

# Option B: Manual install
mkdir -p .windsurf/workflows docs/features
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/speckit-breakdown/main/workflows/speckit.breakdown.md \
  -o .windsurf/workflows/speckit.breakdown.md
```

### Step 3: Create Your Project Spec

Create `docs/PROJECT_SPEC.md`:

```markdown
# My Project Name

## Overview
Brief description of what you're building and why.

## Business Objectives
- Primary objective 1
- Primary objective 2
- Primary objective 3

## Target Users
- **User Type 1**: Description and needs
- **User Type 2**: Description and needs

## Features & Requirements

### Core Features
- **User Authentication**: Register, login, password reset, profile management
- **Dashboard**: Overview metrics, recent activity, quick actions
- **Data Management**: CRUD for main entities, search, filters, export
- **Reporting**: Generate reports, charts, export to PDF/Excel
- **Admin Panel**: User management, system settings, audit logs

### Technical Requirements
- Framework: [Next.js 14, React, Vue, etc.]
- Database: [PostgreSQL, MongoDB, etc.]
- Authentication: [NextAuth, Auth0, etc.]
- Hosting: [Vercel, AWS, etc.]

## Success Criteria
- Handle 10,000+ users
- Sub-2-second page loads
- 99.9% uptime
- Mobile responsive

## Timeline
- Duration: 3 months
- Team: 2 developers
- Launch: Q2 2025
```

### Step 4: Run the Breakdown
```bash
/speckit.breakdown docs/PROJECT_SPEC.md
```

### Step 5: Review Generated Files
```bash
# View master breakdown
cat docs/project-breakdown.md

# List generated features
ls docs/features/
```

### Step 6: Process First Feature
```bash
# Copy command from docs/features/feature-01-*.md
/speckit.specify [paste feature description here]

# Continue SpecKit workflow
/speckit.clarify
/speckit.plan
/speckit.tasks
/speckit.implement
```

## Real Example

### Input: Simple E-commerce Spec
```markdown
# E-commerce Store

## Overview
Online store for selling handmade crafts

## Features
- Product catalog with categories
- Shopping cart and checkout
- User accounts with order history
- Payment via Stripe
- Admin dashboard for inventory
- Email notifications

## Tech Stack
- Next.js 14, PostgreSQL, Prisma
- Stripe, SendGrid
- Deploy to Vercel

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
Full: 11 weeks

Files created:
- docs/project-breakdown.md
- docs/features/feature-01-authentication.md
- docs/features/feature-02-product-catalog.md
- ... and 4 more
```

## Tips for Success

### ✅ DO:
- Provide detailed feature descriptions
- Include user personas
- Specify technical constraints
- Set realistic timelines

### ❌ DON'T:
- Be too vague ("user stuff")
- Skip user stories
- Ignore dependencies
- Estimate without constraints

## Common Issues

### Issue: "No features identified"
**Fix**: Add more detail to your spec. Include specific workflows.

### Issue: "Features too large"
**Fix**: The tool will automatically split them. Review and approve.

### Issue: "Wrong tech stack in features"
**Fix**: Specify your stack clearly in project spec.

## Advanced AI Extensions (006)

Once you have the core SpecKit breakdown and design flow working, you can opt into
the advanced AI extensions defined in `specs/006-ai-extensions/`.

- Use these when you want architecture snapshots, context packs, health reports,
  agent bundles, datasets, dependency graphs, implementation hints, and
  release notes generated from your SpecKit artifacts.
- Start with the feature quickstart:
  - `specs/006-ai-extensions/quickstart.md`
- Typical flow after your specs/plans/tasks are stable:
  - `/speckit.arch`, `/speckit.bundle`, `/speckit.health`, `/speckit.agentize`,
    `/speckit.dataset`, `/speckit.graph`, `/speckit.hint`, `/speckit.release`.

## Next Steps

1. ✅ Install complete
2. 📝 Write project spec
3. 🔄 Run /speckit.breakdown
4. 📋 Review features
5. 🚀 Start with /speckit.specify

**Ready? Create your PROJECT_SPEC.md and run the breakdown!** 🎉
