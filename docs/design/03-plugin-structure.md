# Plugin Structure

## Directory Layout

```
yoshiwatanabe-plugins/
└── memory-plugin/
    ├── plugin.json                    # Plugin manifest
    ├── README.md                      # Installation and usage docs
    ├── LICENSE                        # License file
    │
    ├── skills/                        # Claude Agent Skills
    │   ├── save-memory/
    │   │   └── SKILL.md
    │   ├── describe-repo/
    │   │   └── SKILL.md
    │   ├── find-repo/
    │   │   └── SKILL.md
    │   ├── scan-repos/
    │   │   └── SKILL.md
    │   ├── list-recent-repos/
    │   │   └── SKILL.md
    │   └── search-memory/
    │       └── SKILL.md
    │
    ├── agents/                        # Subagent definitions
    │   └── memory-manager.md
    │
    ├── scripts/                       # Python implementation
    │   ├── __init__.py
    │   ├── requirements.txt
    │   ├── manage_memory.py           # Core memory operations
    │   ├── sync_git.py                # Git synchronization
    │   ├── scan_repos.py              # Local repository discovery
    │   ├── query_memory.py            # Search and query
    │   └── utils.py                   # Common utilities
    │
    ├── install/                       # Installation scripts
    │   ├── install.sh                 # Linux/WSL installation
    │   ├── install.ps1                # Windows installation
    │   └── setup_venv.py              # Python venv setup
    │
    └── tests/                         # Unit tests (optional)
        ├── test_manage_memory.py
        ├── test_sync_git.py
        └── test_query_memory.py
```

## Plugin Manifest: `plugin.json`

```json
{
  "name": "yoshiwatanabe-memory",
  "version": "1.0.0",
  "description": "Personal memory and context management system across machines and repositories",
  "author": "Yoshi Watanabe",
  "repository": "https://github.com/yoshiwatanabe/yoshiwatanabe-plugins",
  "license": "MIT",

  "claude": {
    "minVersion": "0.1.0"
  },

  "skills": [
    {
      "name": "save-memory",
      "description": "Save current session progress and context",
      "file": "skills/save-memory/SKILL.md",
      "scope": "user"
    },
    {
      "name": "describe-repo",
      "description": "Add or update repository metadata",
      "file": "skills/describe-repo/SKILL.md",
      "scope": "user"
    },
    {
      "name": "find-repo",
      "description": "Find clones of a repository across machines",
      "file": "skills/find-repo/SKILL.md",
      "scope": "user"
    },
    {
      "name": "scan-repos",
      "description": "Scan local repositories and compare with tracked repos",
      "file": "skills/scan-repos/SKILL.md",
      "scope": "user"
    },
    {
      "name": "list-recent-repos",
      "description": "List recently worked-on repositories",
      "file": "skills/list-recent-repos/SKILL.md",
      "scope": "user"
    },
    {
      "name": "search-memory",
      "description": "Search memory by feature or work description",
      "file": "skills/search-memory/SKILL.md",
      "scope": "user"
    }
  ],

  "agents": [
    {
      "name": "memory-manager",
      "description": "Manages memory operations in isolated context",
      "file": "agents/memory-manager.md"
    }
  ],

  "scripts": {
    "postinstall": "python install/setup_venv.py"
  },

  "config": {
    "configRepoPath": {
      "description": "Path to yoshiwatanabe-configurations repository",
      "type": "string",
      "default": "C:\\Users\\{username}\\repos\\yoshiwatanabe-configurations"
    },
    "detailLevel": {
      "description": "Default detail level for memory summaries",
      "type": "string",
      "enum": ["brief", "normal", "detailed"],
      "default": "normal"
    },
    "autoSync": {
      "description": "Automatically sync with remote after operations",
      "type": "boolean",
      "default": true
    }
  }
}
```

## Installation Process

### 1. Linux/WSL Installation: `install.sh`

```bash
#!/bin/bash
set -e

PLUGIN_DIR="$HOME/.claude/plugins/yoshiwatanabe-memory"

echo "Installing yoshiwatanabe-memory plugin..."

# Create plugin directory
mkdir -p "$PLUGIN_DIR"

# Copy plugin files
cp -r ./* "$PLUGIN_DIR/"

# Setup Python venv
cd "$PLUGIN_DIR"
python3 -m venv venv
source venv/bin/activate
pip install -r scripts/requirements.txt

echo "Installation complete!"
echo "Plugin installed to: $PLUGIN_DIR"
echo ""
echo "Next steps:"
echo "1. Clone yoshiwatanabe-configurations to ~/repos/ (or C:/Users/<user>/repos/ on Windows)"
echo "2. Configure config repo path: claude config set yoshiwatanabe-memory.configRepoPath <path>"
echo "3. Use skills: /save-memory, /search-memory, etc."
```

### 2. Windows Installation: `install.ps1`

```powershell
$ErrorActionPreference = "Stop"

$PLUGIN_DIR = "$env:USERPROFILE\.claude\plugins\yoshiwatanabe-memory"

Write-Host "Installing yoshiwatanabe-memory plugin..." -ForegroundColor Green

# Create plugin directory
New-Item -ItemType Directory -Force -Path $PLUGIN_DIR | Out-Null

# Copy plugin files
Copy-Item -Path .\* -Destination $PLUGIN_DIR -Recurse -Force

# Setup Python venv
Set-Location $PLUGIN_DIR
python -m venv venv
& .\venv\Scripts\Activate.ps1
pip install -r scripts\requirements.txt

Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "Plugin installed to: $PLUGIN_DIR"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Clone yoshiwatanabe-configurations to C:\Users\<user>\repos\"
Write-Host "2. Configure config repo path: claude config set yoshiwatanabe-memory.configRepoPath <path>"
Write-Host "3. Use skills: /save-memory, /search-memory, etc."
```

### 3. Python venv Setup: `setup_venv.py`

```python
#!/usr/bin/env python3
import sys
import subprocess
import os
from pathlib import Path

def setup_venv():
    """Set up Python virtual environment and install dependencies."""
    plugin_dir = Path(__file__).parent.parent
    venv_dir = plugin_dir / "venv"
    requirements = plugin_dir / "scripts" / "requirements.txt"

    print("Setting up Python virtual environment...")

    # Create venv
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

    # Determine pip path
    if sys.platform == "win32":
        pip_path = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_path = venv_dir / "bin" / "pip"

    # Install dependencies
    print("Installing dependencies...")
    subprocess.run([str(pip_path), "install", "-r", str(requirements)], check=True)

    print("Virtual environment setup complete!")

if __name__ == "__main__":
    setup_venv()
```

## Python Dependencies: `requirements.txt`

```txt
# Git operations
gitpython>=3.1.40

# YAML parsing
PyYAML>=6.0

# CLI framework (optional, for future enhancements)
click>=8.1.0

# Cross-platform path handling (built-in, no install needed)
# pathlib

# Testing (optional)
pytest>=7.4.0
pytest-cov>=4.1.0
```

## Plugin Configuration

Users configure the plugin via Claude CLI:

```bash
# Set config repo path
claude config set yoshiwatanabe-memory.configRepoPath "C:\\Users\\twatana\\repos\\yoshiwatanabe-configurations"

# Set default detail level
claude config set yoshiwatanabe-memory.detailLevel normal

# Enable auto-sync
claude config set yoshiwatanabe-memory.autoSync true
```

Or via config file: `~/.claude/config.json`

```json
{
  "plugins": {
    "yoshiwatanabe-memory": {
      "configRepoPath": "C:\\Users\\twatana\\repos\\yoshiwatanabe-configurations",
      "detailLevel": "normal",
      "autoSync": true
    }
  }
}
```

## Directory Structure After Installation

### Windows
```
C:\Users\twatana\
├── .claude\
│   ├── config.json
│   └── plugins\
│       └── yoshiwatanabe-memory\
│           ├── plugin.json
│           ├── skills\
│           ├── agents\
│           ├── scripts\
│           └── venv\          # Python virtual environment
└── repos\
    └── yoshiwatanabe-configurations\   # Config repo (shared with WSL)
        └── memory\
```

### WSL/Linux
```
/home/twatana/
├── .claude/
│   ├── config.json
│   └── plugins/
│       └── yoshiwatanabe-memory/
│           ├── plugin.json
│           ├── skills/
│           ├── agents/
│           ├── scripts/
│           └── venv/          # Python virtual environment
└── (accesses Windows config repo via /mnt/c/Users/twatana/repos/yoshiwatanabe-configurations)
```

## Key Design Decisions

1. **User-scope installation:** Plugin available in all Claude sessions for that user
2. **Separate venv per environment:** Each OS environment (Windows/WSL) has its own venv
3. **Shared config repo:** Both Windows and WSL on same machine access same local clone
4. **Configurable paths:** Users can customize config repo location
5. **Standalone scripts:** Python scripts can be run independently for testing/debugging
