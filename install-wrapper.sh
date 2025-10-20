#!/bin/bash
# SpecKit Breakdown Installer Wrapper
# Downloads and runs the interactive installer

set -e

TEMP_INSTALLER="/tmp/speckit-breakdown-installer-$$.sh"

echo "📥 Downloading installer..."
curl -fsSL "https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/install.sh" -o "$TEMP_INSTALLER"

chmod +x "$TEMP_INSTALLER"

echo ""
exec "$TEMP_INSTALLER"
