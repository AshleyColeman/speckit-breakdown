# SpecKit Breakdown - Project to Features Tool

**Transform complete project specifications into individual, well-scoped features ready for SpecKit processing.**

## What It Does

Takes your complete project plan (with all features mixed together) and intelligently breaks it down into 5-12 independent features, each with:
- ✅ Clear scope (1.5-3 weeks each)
- ✅ 3-6 focused user stories
- ✅ Success criteria & dependencies
- ✅ Ready for `/speckit.specify`

## Installation

### Prerequisites

1. **SpecKit workflows installed** in your project
   - You should already have `.windsurf/workflows/` folder
   - Official SpecKit workflows: `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, etc.
   - **How to install**:
     ```bash
     uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
     specify init
     ```

### Quick Install

```bash
# Navigate to your project root
cd /path/to/your/project

# Download and run the interactive installer
curl -fsSL https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/install.sh -o install-speckit-breakdown.sh
chmod +x install-speckit-breakdown.sh
./install-speckit-breakdown.sh

# Clean up after installation
rm install-speckit-breakdown.sh
```

### Installer supply-chain guidance

- **Review before running**: Prefer downloading the installer to a file, reviewing it, then executing it.
- **Pin what you run**: For long-lived setups, pin the installer/workflow downloads to a specific release tag or commit SHA.
- **Verify integrity (optional)**: If you publish checksums/signatures for releases, verify them before executing.

Pinned install example (replace `vX.Y.Z` with a tag or commit SHA):

```bash
REF=vX.Y.Z
curl -fsSL "https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/${REF}/install.sh" -o /tmp/sb-install.sh
less /tmp/sb-install.sh
chmod +x /tmp/sb-install.sh
SPECKIT_BREAKDOWN_REF="${REF}" /tmp/sb-install.sh
rm /tmp/sb-install.sh
```

**One-liner (downloads, runs, and cleans up):**
```bash
curl -fsSL https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/install.sh -o /tmp/sb-install.sh && chmod +x /tmp/sb-install.sh && /tmp/sb-install.sh && rm /tmp/sb-install.sh
```

Or manual installation:

```bash
# 1. Copy the workflow
cp workflows/speckit.breakdown.md /path/to/your/project/.windsurf/workflows/

# 2. Create features directory
mkdir -p /path/to/your/project/docs/features

# 3. Done! Now you can use /speckit.breakdown
```

## Documentation

- **[System Guide (Gold Standard)](docs/speckit_system_guide.md)**: The technical reference and "Golden Workflow" for the entire system.
- **[Exist Project Guide (Dummies Guide)](docs/guides/EXISTING_PROJECT_GUIDE.md)**: **<-- START HERE for brownfield projects.**
- **[Quick Start](docs/guides/QUICK_START.md)**: 5-minute guide.
- **[Installation Guide](docs/guides/INSTALLATION_GUIDE.md)**: Detailed installation steps.
- **[How to Use](docs/guides/HOW_TO_USE.md)**: Usage guide and examples.
- **[Get Started](docs/guides/GET_STARTED.md)**: Local development guide.
- **[Maintainer Guide](docs/maintainers/SETUP_AS_REPO.md)**: Publishing and maintenance.

## Support Matrix

| Component | Support Tier | Notes |
|---|---|---|
| Markdown workflows (`/speckit.*`) | Stable | Runs as Windsurf/SpecKit workflows. |
| Python CLI (`speckit.db.prepare`) | Stable | Run via `python -m src.cli.main speckit.db.prepare`. |
| Data store: SQLite | Stable (default) | Auto-initializes schema on first run. |
| Data store: PostgreSQL | Experimental (disabled by default) | Requires `--enable-experimental-postgres` and a pre-existing schema contract. |

## Data store schema expectations

- **SQLite**: The CLI creates/updates the `.speckit/db.sqlite` file and initializes required tables automatically.
- **PostgreSQL**: The CLI will refuse to run unless the target database already matches the expected schema contract (including `tasks.metadata` being `json/jsonb` and supporting `metadata->>'code'` lookups for stable identifiers).

## Python CLI (Developer)

To run the Python CLI deterministically:

```bash
pip install -r requirements-dev.txt
python -m src.cli.main speckit.db.prepare
```

## Usage

### Step 1: Create Your Project Spec

Create a file like `docs/PROJECT_SPEC.md` with your complete project requirements:

```markdown
# My Awesome Project

## Overview
[What you're building and why]

## Business Objectives
- Objective 1
- Objective 2

## Target Users
- User type 1: [description]
- User type 2: [description]

## Features & Requirements
- Feature 1 with details
- Feature 2 with details
- Feature 3 with details
[... all your features mixed together]

## Technical Stack
- Framework: Next.js / React / etc.
- Database: PostgreSQL / MongoDB / etc.

## Timeline
- Target: 3 months
- Team: 2 developers
```

### Step 2: Run the Breakdown

```bash
/speckit.breakdown docs/PROJECT_SPEC.md
```

Or with inline description:

```bash
/speckit.breakdown I have a project spec in docs/MY_SPEC.md that describes an e-commerce platform
```

### Step 3: Review Generated Files

The tool creates:

```
docs/
├── project-breakdown.md           # Master breakdown with all features
└── features/
    ├── feature-01-description.md  # Individual feature files
    ├── feature-02-description.md
    ├── feature-03-description.md
    └── quick-start.sh            # Commands to run
```

### Step 4: Process Each Feature

```bash
# Start with Feature 1
/speckit.specify [content from feature-01-description.md]

# Then continue the SpecKit workflow
/speckit.clarify
/speckit.plan
/speckit.tasks
/speckit.orchestrate

# Sync to the system brain (required for implementing tasks)
python -m src.cli.main --verbose

/speckit.implement
```

## Example: From Project → Features

### Before (Your Spec)
```markdown
# E-commerce Platform

I want to build a platform with:
- User authentication (login, register, profile)
- Product catalog (browse, search, filter)
- Shopping cart (add items, checkout)
- Payment processing (Stripe, PayPal)
- Admin dashboard (manage products, orders)
- Email notifications
```

### After (Generated Features)
```
F01: User Authentication System (P1, 2 weeks)
F02: Product Catalog Browser (P1, 2.5 weeks)
F03: Shopping Cart & Checkout (P1, 2.5 weeks)
F04: Payment Integration (P1, 2 weeks)
F05: Admin Dashboard (P2, 3 weeks)
F06: Email Notification System (P3, 1.5 weeks)

MVP: F01-F04 (9 weeks)
Total: 13.5 weeks
```

## What Makes Good Features?

The breakdown follows these principles:

### ✅ Good Feature Characteristics
- **Clear User Value**: Users can see and use it
- **Complete Workflow**: Full user journey start to finish
- **Right Size**: 1.5-3 weeks of work
- **Testable**: Can verify it works independently
- **Minimal Dependencies**: Mostly independent development

### ✅ Good Examples
- "User Authentication System" (complete login/register flow)
- "Product Search & Browse" (full product discovery)
- "Shopping Cart & Checkout" (complete purchase workflow)

### ❌ Bad Examples (Too Technical/Small/Large)
- "Database Layer" (too technical, not user-facing)
- "Login Button" (too small, part of larger feature)
- "Entire E-commerce Platform" (too large, needs breakdown)

## Configuration

You can customize the breakdown by editing `.windsurf/workflows/speckit.breakdown.md`:

```markdown
### Feature Sizing
- Ideal: 1.5-3 weeks
- Min: 1 week
- Max: 3 weeks (split if larger)

### Feature Count
- Target: 5-12 features per project
- MVP: 3-6 features (8-12 weeks)
```

## Tips for Best Results

### 1. Write a Detailed Project Spec
The more detail you provide, the better the breakdown:

✅ **Good**: 
```markdown
## User Authentication
- Email/password registration with verification
- Login with session management (7-day sessions)
- Profile page with avatar upload and bio
- Password reset via email
- Role-based permissions (Admin, User)
```

❌ **Too Vague**:
```markdown
## Features
- User stuff
- Products
```

### 2. Include User Personas
```markdown
## Target Users
- **Shoppers**: Browse and purchase products
- **Admins**: Manage inventory and orders
- **Vendors**: Add and manage their products
```

### 3. Specify Technical Constraints
```markdown
## Technical Requirements
- Must use Next.js 14+ App Router
- PostgreSQL database with Prisma
- Real-time updates required
- Support 10,000+ concurrent users
```

### 4. Set Realistic Timeline
```markdown
## Timeline
- Total: 3 months
- Team: 2 developers, 1 designer
- Launch: End of Q2 2025
```

## Troubleshooting

### "No features identified"
**Solution**: Add more detail to your project spec. Include specific user workflows and requirements.

### "Too many features generated"
**Solution**: Focus on MVP first. You can always run breakdown again for Phase 2 features.

### "Features have circular dependencies"
**Solution**: The tool will detect this and suggest splitting shared functionality into a foundation feature.

### "Estimates seem off"
**Solution**: Complete one feature fully, then use that to calibrate remaining estimates.

### Data store support tiers

- **SQLite**: Stable (default).
- **PostgreSQL**: Experimental and disabled by default. To use it with `speckit.db.prepare`, pass `--db-url` and `--enable-experimental-postgres`.

## Integration with SpecKit

This tool is designed to work seamlessly with the full SpecKit workflow:

```
1. /speckit.breakdown     → Break project into features
2. /speckit.specify       → Create detailed spec for each feature
3. /speckit.clarify       → Resolve ambiguities
4. /speckit.plan          → Generate implementation plan
5. /speckit.tasks         → Create task breakdown
6. /speckit.orchestrate     → Calculate Step Order
7. python -m src.cli.main → Sync to system brain
8. /speckit.implement     → Execute implementation
```

## Examples

See the `examples/` directory for complete examples:
- E-commerce platform breakdown
- SaaS dashboard breakdown
- Mobile app breakdown
- Admin panel breakdown

## Support

- Issues: https://github.com/AshleyColeman/speckit-breakdown/issues
- Discussions: https://github.com/AshleyColeman/speckit-breakdown/discussions

## License

MIT License - Feel free to use in any project!

## Credits

Built to complement the official SpecKit system.
Optimized for Windsurf IDE and Cascade AI.
