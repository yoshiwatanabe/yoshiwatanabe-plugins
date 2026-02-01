$ErrorActionPreference = "Stop"

$PLUGIN_DIR = "$env:USERPROFILE\.claude\plugins\yoshiwatanabe-dev"

Write-Host "Installing yoshiwatanabe-dev plugin..." -ForegroundColor Green

# Create plugin directory
New-Item -ItemType Directory -Force -Path $PLUGIN_DIR | Out-Null

# Copy plugin files
Copy-Item -Path ..\skills -Destination $PLUGIN_DIR -Recurse -Force
Copy-Item -Path ..\scripts -Destination $PLUGIN_DIR -Recurse -Force
Copy-Item -Path ..\agents -Destination $PLUGIN_DIR -Recurse -Force
Copy-Item -Path ..\requirements.txt -Destination $PLUGIN_DIR -Force
Copy-Item -Path ..\plugin.json -Destination $PLUGIN_DIR -Force

# Setup Python venv
Set-Location $PLUGIN_DIR
python -m venv venv
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host "Plugin installed to: $PLUGIN_DIR"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Ensure your configuration repository has the domain structure:"
Write-Host "   - domains/dev/memory/episodes/"
Write-Host "   - domains/dev/memory/repositories/"
Write-Host ""
Write-Host "2. Configure the plugin:"
Write-Host "   claude config set yoshiwatanabe-dev.configRepoPath <path-to-your-config-repo>"
Write-Host ""
Write-Host "3. Use the skills:"
Write-Host "   /save-memory - Save coding session"
Write-Host "   /describe-repo - Add repository metadata"
Write-Host "   /find-repo - Find repo clones"
Write-Host "   /scan-repos - Discover repositories"
Write-Host "   /list-recent-repos - Show recent work"
Write-Host "   /search-memory - Search by keywords"
