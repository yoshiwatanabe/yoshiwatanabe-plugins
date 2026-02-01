#!/bin/bash
set -e

PLUGIN_DIR="$HOME/.claude/plugins/yoshiwatanabe-dev"

echo "Installing yoshiwatanabe-dev plugin..."

# Create plugin directory
mkdir -p "$PLUGIN_DIR"

# Copy plugin files
cp -r ../skills "$PLUGIN_DIR/"
cp -r ../scripts "$PLUGIN_DIR/"
cp -r ../agents "$PLUGIN_DIR/"
cp ../requirements.txt "$PLUGIN_DIR/"
cp ../plugin.json "$PLUGIN_DIR/"

# Setup Python venv
cd "$PLUGIN_DIR"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo "Plugin installed to: $PLUGIN_DIR"
echo ""
echo "Next steps:"
echo "1. Ensure your configuration repository has the domain structure:"
echo "   - domains/dev/memory/episodes/"
echo "   - domains/dev/memory/repositories/"
echo ""
echo "2. Configure the plugin:"
echo "   claude config set yoshiwatanabe-dev.configRepoPath <path-to-your-config-repo>"
echo ""
echo "3. Use the skills:"
echo "   /save-memory - Save coding session"
echo "   /describe-repo - Add repository metadata"
echo "   /find-repo - Find repo clones"
echo "   /scan-repos - Discover repositories"
echo "   /list-recent-repos - Show recent work"
echo "   /search-memory - Search by keywords"
