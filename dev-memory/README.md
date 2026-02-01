# yoshiwatanabe-dev

Development domain memory management plugin for Claude Code.

Track your coding sessions, repositories, and development work across multiple machines with persistent memory.

## Features

- 📝 **Save coding sessions** - Capture progress, goals, and context
- 📦 **Repository metadata** - Describe repos with tags and notes
- 🔍 **Find repo clones** - Locate repositories across machines
- 🔎 **Search memory** - Find past work by keywords
- 📊 **Scan repositories** - Discover untracked repos
- 📅 **Recent activity** - See what you worked on recently

## Installation

### Prerequisites

- Python 3.8+
- Claude Code CLI
- A configuration repository with domain structure (see Setup below)

### Install Plugin

**Linux/WSL:**
```bash
cd install
chmod +x install.sh
./install.sh
```

**Windows:**
```powershell
cd install
.\install.ps1
```

### Configure

Set the path to your configuration repository:
```bash
claude config set yoshiwatanabe-dev.configRepoPath "/path/to/your-config-repo"
```

## Configuration Repository Setup

Your configuration repository needs this structure:

```
your-config-repo/
├── domains/
│   └── dev/
│       └── memory/
│           ├── episodes/        # Coding session memory
│           ├── repositories/    # Repository metadata
│           ├── machines/        # Machine configs
│           └── index/          # Search indices (optional)
└── machines/                   # Cross-domain machine configs
```

**Example:** Clone and set up a config repo:
```bash
# Create your config repo
git clone https://github.com/yourusername/your-config-repo.git
cd your-config-repo

# Create domain structure
mkdir -p domains/dev/memory/{episodes,repositories,machines,index}
mkdir -p machines

# Initialize as git repo (if new)
git init
git remote add origin https://github.com/yourusername/your-config-repo.git
```

## Skills

### `/save-memory`
Save your current coding session progress.

**Example:** "hey remember the progress in this session"

Captures:
- Current repository, branch, commit
- Machine and OS
- Session summary and keywords
- Goals and next steps

### `/describe-repo`
Add metadata to a repository.

**Example:** "This repo contains the auth service. It requires security team approval for PRs."

### `/find-repo`
Find where a repository is cloned across your machines.

**Example:** "where else do I have clones of this repo?"

### `/scan-repos`
Discover repositories on your machine that aren't being tracked.

**Example:** "scan my repos and show what's not tracked"

### `/list-recent-repos`
Show recently accessed repositories across all machines.

**Example:** "show me 5 repos I worked on recently"

### `/search-memory`
Search your development memory by keywords.

**Example:** "I worked on Azure key vault isolation, which repo was that?"

## Documentation

- [Architecture Overview](docs/design/01-architecture-overview.md)
- [Data Model](docs/design/02-data-model.md)
- [Python Implementation](docs/design/06-python-implementation.md)

## Python Scripts

Scripts can also be run directly for testing:

```bash
cd ~/.claude/plugins/yoshiwatanabe-dev
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows

# Save memory episode
python scripts/manage_memory.py save --config-repo /path/to/config ...

# Query repositories
python scripts/query_memory.py find-repo --config-repo /path/to/config ...

# Scan local repos
python scripts/scan_repos.py scan-repos --config-repo /path/to/config ...
```

## How It Works

1. **Skills** define Claude Code commands (YAML frontmatter + Markdown)
2. **Subagent** (memory-manager) handles operations in isolated context
3. **Python scripts** perform git operations, save/query memory
4. **Data** stored in your config repo's `domains/dev/memory/` directory
5. **Git sync** keeps memory synchronized across machines

## Cross-Platform

Works on:
- ✅ Windows
- ✅ WSL (Windows Subsystem for Linux)
- ✅ Linux
- ✅ macOS

## Domain-Focused

This plugin focuses on the **development domain**. Other plugins can be created for other life domains:
- `yoshiwatanabe-health` - Health and medical tracking
- `yoshiwatanabe-vehicles` - Car/boat maintenance
- `yoshiwatanabe-finance` - Financial planning

Each domain is independent with its own memory structure.

## License

MIT

## Contributing

Issues and PRs welcome at: https://github.com/yoshiwatanabe/yoshiwatanabe-plugins
