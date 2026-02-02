# Architecture Overview

## System Components

### 1. Data Storage (Private Repo)
**Repository:** `yoshiwatanabe-configurations` (current repo)
**Location per machine:** `C:\Users\<user>\repos\yoshiwatanabe-configurations`
**Access:** Both Windows and WSL use same location via `/mnt/c/Users/<user>/repos/yoshiwatanabe-configurations`

**Structure:**
```
yoshiwatanabe-configurations/
├── memory/
│   ├── episodes/           # Memory episode skills (YAML + content)
│   ├── repositories/       # Repository metadata
│   ├── machines/           # Machine-specific state
│   └── index/             # Search indices (optional)
├── config/
│   └── cars/              # Future: other personal configurations
│   └── financial/         # Future: other personal configurations
└── design-artifacts/      # Temporary design docs
```

### 2. Plugin/Logic (Public Repo)
**Repository:** `yoshiwatanabe-plugins`
**Installation:** Per-user `.claude` directory
- Windows: `C:\Users\<user>\.claude/plugins/yoshiwatanabe-memory/`
- WSL: `/home/<user>/.claude/plugins/yoshiwatanabe-memory/`

**Structure:**
```
yoshiwatanabe-plugins/
└── memory-plugin/
    ├── plugin.json                    # Plugin manifest
    ├── skills/
    │   ├── save-memory.md            # Save session progress
    │   ├── describe-repo.md          # Add repo metadata
    │   ├── find-repo.md              # Query repo clones
    │   ├── scan-repos.md             # Discover untracked repos
    │   ├── list-recent-repos.md      # Recent activity
    │   └── search-memory.md          # Search by feature/work
    ├── agents/
    │   └── memory-manager.md         # Subagent definition
    ├── scripts/
    │   ├── requirements.txt          # Python dependencies
    │   ├── manage_memory.py          # Core memory operations
    │   ├── sync_git.py               # Git pull/push/rebase
    │   ├── scan_repos.py             # Local repo discovery
    │   └── query_memory.py           # Search/query logic
    └── install.sh / install.ps1      # Setup scripts
```

### 3. User Environments
**Total: 6 environments**
- Work main machine: Windows + WSL
- Work devbox: Windows + WSL
- Personal PC: Windows + WSL

**Each environment:**
- Installs plugin to `.claude/plugins/yoshiwatanabe-memory/`
- Sets up Python venv in plugin directory
- Accesses same local config repo per machine

## Data Flow

### Save Memory (Use Case 1)
```
User: "hey remember the progress in this session"
  ↓
Main Session: Invokes /save-memory skill
  ↓
Skill: Spawns memory-manager subagent
  ↓
Subagent:
  1. Collects session context (repo, branch, worktree, OS, machine)
  2. Generates summary (configurable detail)
  3. Calls Python script: manage_memory.py save
  4. Python script:
     - git pull (or rebase) from remote
     - Creates memory episode skill (YAML frontmatter + content)
     - Saves to config-repo/memory/episodes/
     - git commit + push
  5. Returns confirmation
  ↓
Main Session: Displays confirmation
```

### Query Memory (Use Case 6)
```
User: "I worked on Azure key vault isolation, which repo?"
  ↓
Main Session: Invokes /search-memory skill
  ↓
Skill: Spawns memory-manager subagent
  ↓
Subagent:
  1. Calls Python script: query_memory.py search-memory --keywords "Azure key vault isolation"
  2. Python script:
     - Scans memory/episodes/*.md for matching YAML frontmatter + content
     - Returns matching episodes with repo, branch, commit, date
  3. Returns results
  ↓
Main Session: Displays results
```

## Synchronization Strategy

### Local-to-Remote Sync
- Before writes: `git pull` (or `git rebase` if conflicts)
- After writes: `git commit + push`
- Background: Periodic `git fetch` (optional, via cron or scheduled task)

### Conflict Resolution
- Contributions from different machines usually disjoint (different files)
- Use `git rebase` to keep linear history
- If conflicts occur, manual resolution required

## Technology Stack

- **Language:** Python 3.8+
- **Environment:** venv per user
- **Libraries:**
  - `gitpython` - Git operations
  - `PyYAML` - YAML frontmatter
  - `pathlib` - Cross-platform paths
  - `click` - CLI framework (optional)
- **Claude Integration:**
  - Skills (`.md` files with YAML frontmatter)
  - Subagents (agent definitions)
  - Plugin manifest (`plugin.json`)

## Key Design Decisions

1. **Python + venv:** Cross-platform, isolated, rich ecosystem
2. **Single local clone per machine:** Avoid duplication, both Windows/WSL access same copy
3. **YAML frontmatter for indexing:** Efficient context loading, progressive disclosure
4. **Subagent isolation:** Memory operations don't pollute main session
5. **Git-based sync:** Simple, proven, leverages existing GitHub infrastructure
6. **Extensible structure:** Config repo can grow beyond dev memory (cars, finance, etc.)
