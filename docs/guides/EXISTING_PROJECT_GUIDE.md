# Dummies Guide: Adding SpecKit to an Existing Project

So you have an **existing code base** (a "Brownfield" project) and you want to start using SpecKit to build new features without breaking everything?

This guide walks you through:
1.  **Pulling** the SpecKit commands into your project.
2.  **Setting up** the Database.
3.  **Running** a small MVP feature to test the waters.

---

## 🛑 Step 0: The "Before You Start" Checklist

Make sure you are in the **root directory** of your existing project:

```bash
cd /path/to/my-existing-app
ls -la
# You should see your package.json, requirements.txt, src/, etc.
```

---

## 📥 Step 1: Pull the SpecKit Commands

Run this **one-liner** to verify your environment and install the necessary workflows (`/speckit.*`) and scripts into your `.windsurf/workflows/` folder.

```bash
curl -fsSL https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/install.sh | bash
```

**What just happened?**
- Created `.windsurf/workflows/` (if missing).
- Downloaded `speckit.breakdown.md` and other core workflows.
- Created `docs/features/` folder.

---

## 📝 Step 2: Define Your MVP (The "Toe Dip")

Don't try to SpecKit your *entire* existing codebase at once. Start with a small **MVP Feature** to get comfortable.

Create a file at `docs/MVP.md`:

```markdown
# MVP: Refactor User Profile
> **Goal**: Modernize the user profile page to match the new design system.

## Business Objectives
- Improve user engagement.
- Fix layout bugs on mobile.

## Features & Requirements
### F-01: Update Profile UI
- **User Story**: As a user, I want a responsive profile page so I can view my data on mobile.
- **Constraints**: Must use existing `UserService` class.
- **Tech**: React components in `src/components/profile/`.

## Success Criteria
- Mobile score > 90 on Lighthouse.
- All existing tests pass.
```

---

## 🏃 Step 3: Run the Breakdown

Turn that simple MVP doc into SpecKit features:

```bash
/speckit.breakdown docs/MVP.md
```

**Output**:
- You'll see `docs/project-breakdown.md` created.
- You'll see `docs/features/feature-01-update-profile-ui.md` created.

---

## 🧠 Step 4: Sync to the "Brain" (The Database)

This is the most important step for an existing project. You need to load your new docs into the SpecKit database so the AI knows what to build.

**1. Create the detailed spec & plan:**
```bash
/speckit.specify docs/features/feature-01-update-profile-ui.md
/speckit.plan
/speckit.tasks
```

**2. Push to the Database:**
```bash
# This reads your project files and populates the local SQLite DB
/speckit.db.prepare
```

**Why do this?**
- Validates that your tasks don't have circular dependencies.
- Assigns specific Step Orders (Step 1, Step 2b, etc.).
- Prepares the context for the Coding Agent.

---

## 👩‍💻 Step 5: Implement (The Magic)

Now that the DB is prepped, run the implementation loop on your tasks:

```bash
# This grabs the simplified tasks from the DB and writes code
/speckit.implement
```

---

## 🧹 Summary Checklist

1.  [ ] **Install**: Run the `curl` installer in project root.
2.  [ ] **MVP Spec**: Create `docs/MVP.md`.
3.  [ ] **Breakdown**: `/speckit.breakdown docs/MVP.md`.
4.  [ ] **Plan**: `/speckit.specify` -> `/speckit.plan` -> `/speckit.tasks`.
5.  [ ] **Database**: `/speckit.db.prepare` (Crucial!).
6.  [ ] **Code**: `/speckit.implement`.

**You are now running SpecKit on your existing project!** 🚀
