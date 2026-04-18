#!/usr/bin/env bash
# fundamentals-desk — install/sync script
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_DIR="$HOME/.claude/skills/fundamentals-desk"
STALE_ZIP="$HOME/.claude/skills/fundamentals-desk.skill"

echo "📦 fundamentals-desk install/sync"
echo "   source: $REPO_DIR"
echo "   target: $INSTALL_DIR"

if ! python3 -c "import yfinance" 2>/dev/null; then
  echo "📦 Installing yfinance..."
  pip3 install yfinance || { echo "❌ yfinance install failed"; exit 1; }
fi

[ -f "$STALE_ZIP" ] && { echo "🗑️  removing stale $STALE_ZIP"; rm "$STALE_ZIP"; }

if [ "${1:-}" = "--clean" ]; then
  echo "🧹 clean install"
  rm -rf "$INSTALL_DIR"
fi

mkdir -p "$INSTALL_DIR"
cp "$REPO_DIR/SKILL.md" "$INSTALL_DIR/"
cp -R "$REPO_DIR/scripts" "$INSTALL_DIR/"
[ -d "$REPO_DIR/data" ] && cp -R "$REPO_DIR/data" "$INSTALL_DIR/"

VERSION=$(grep -m1 "^version:" "$INSTALL_DIR/SKILL.md" | awk '{print $2}')
echo "✅ installed fundamentals-desk v$VERSION — restart Claude Code to reload"
