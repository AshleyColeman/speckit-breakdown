#!/usr/bin/env bats

setup() {
    # Create a dummy project directory
    TEST_DIR="$(mktemp -d)"
    PROJECT_DIR="$TEST_DIR/my-project"
    mkdir -p "$PROJECT_DIR"
    
    # Path to local installer
    INSTALLER_SCRIPT="$BATS_TEST_DIRNAME/../../scripts/install/install-local.sh"
}

teardown() {
    rm -rf "$TEST_DIR"
}

@test "install-local.sh fails if .windsurf/workflows is missing" {
    cd "$PROJECT_DIR"
    # Ensure directory does NOT exist
    rm -rf .windsurf
    
    run bash "$INSTALLER_SCRIPT"
    
    [ "$status" -eq 1 ]
    [[ "$output" == *"Error: .windsurf/workflows directory not found"* ]]
}

@test "install-local.sh creates .windsurf/workflows directory handling" {
    # This test is somewhat redundant if we assume the user follows instructions,
    # but let's test the Happy Path where prereqs exist
    cd "$PROJECT_DIR"
    mkdir -p .windsurf/workflows
    
    run bash "$INSTALLER_SCRIPT"
    
    [ "$status" -eq 0 ]
    [ -d "docs/features" ]
}

@test "install-local.sh copies workflow file" {
    cd "$PROJECT_DIR"
    mkdir -p .windsurf/workflows
    
    run bash "$INSTALLER_SCRIPT"
    
    [ "$status" -eq 0 ]
    [ -f ".windsurf/workflows/speckit.breakdown.md" ]
}
