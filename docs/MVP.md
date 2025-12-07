# MVP Project: CLI Note Taker
> **Purpose**: A small, complete project to validate the SpecKit "Golden Workflow" end-to-end.

## 1. Overview
A simple Command Line Interface (CLI) application that allows users to capture, list, and delete quick text notes. The app stores notes in a local JSON file.

## 2. Business Objectives
- Demonstrate a complete software lifecycle using SpecKit.
- Validate that `db.prepare` correctly handles dependencies and step ordering.
- Produce a working artifact in under 30 minutes of agent time.

## 3. Target Users
- Developers needing a quick scratchpad.
- SpecKit maintainers testing the system.

## 4. Features

### Feature 1: Note Management
**ID**: `FEAT-01`
- **User Story 1**: As a user, I want to add a note so I don't forget ideas.
- **User Story 2**: As a user, I want to list all my notes to review them.
- **User Story 3**: As a user, I want to delete a note by ID when I'm done.

### Feature 2: Data Persistence
**ID**: `FEAT-02`
- **User Story 1**: As a system, I want to load/save notes to `~/.notes.json` automatically.

## 5. Technical Constraints
- **Language**: Python 3.10+
- **Interface**: Typer (CLI library)
- **Storage**: JSON file (No database compliant for simplicity)
- **Testing**: Pytest

## 6. Success Criteria
1.  Can add a note: `notes add "Hello World"`
2.  Can list notes: `notes list` (Shows ID: 1 | Hello World)
3.  Can delete note: `notes delete 1`
