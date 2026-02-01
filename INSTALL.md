# Installation Guide

Simple 3-step installation using Claude Code.

## Prerequisites

- Claude Code CLI installed
- A configuration repository with domain structure (see [Configuration Setup](#configuration-setup))

## Installation Steps

### 1. Add the Marketplace

```
/plugin marketplace add yoshiwatanabe/yoshiwatanabe-plugins
```

### 2. Install the Plugin

```
/plugin install yoshiwatanabe-dev@yoshiwatanabe-plugins
```

### 3. Configure the Plugin

Add the configuration repository path to your Claude Code settings.

Edit `~/.claude/settings.json` and add the `env` section:

**Windows:**
```json
{
  "env": {
    "YW_CONFIG_REPO_PATH": "C:\\Users\\<username>\\Repos\\yoshiwatanabe-configurations"
  }
}
```

**WSL/Linux:**
```json
{
  "env": {
    "YW_CONFIG_REPO_PATH": "/home/<username>/repos/yoshiwatanabe-configurations"
  }
}
```

**Note:** If you have other environment variables, merge them into the existing `env` object.

## Verify Installation

Check that all skills are available:
- `/save-memory` - Save coding session progress
- `/describe-repo` - Add repository metadata
- `/find-repo` - Find repo clones across machines
- `/scan-repos` - Discover local repositories
- `/list-recent-repos` - Show recent work
- `/search-memory` - Search by keywords
- `/archive-repo` - Hide obsolete repositories
- `/unarchive-repo` - Restore archived repositories

## Configuration Setup

Your configuration repository should have this structure:

```
yoshiwatanabe-configurations/
├── domains/
│   └── dev/
│       └── memory/
│           ├── episodes/        # Coding session memory
│           ├── repositories/    # Repository metadata
│           └── machines/        # Machine configs
└── machines/                   # Cross-domain machine configs
```

If you don't have this structure yet:

```bash
cd /path/to/your-config-repo
mkdir -p domains/dev/memory/{episodes,repositories,machines}
mkdir -p machines
git add .
git commit -m "Initialize domain structure"
git push
```

## Multiple Machines

Repeat steps 1-3 on each machine. The plugin will sync memory across all machines via your configuration repository.

## Troubleshooting

**Plugin not found:**
- Ensure the marketplace was added successfully: `claude config get marketplaces`
- Try adding with full URL: `/plugin marketplace add https://github.com/yoshiwatanabe/yoshiwatanabe-plugins.git`

**Skills not showing:**
- Restart Claude Code
- Check plugin is enabled: `claude config get enabledPlugins`

**Python errors:**
- The plugin automatically sets up its virtual environment
- If issues persist, check Python 3.8+ is installed: `python --version`
