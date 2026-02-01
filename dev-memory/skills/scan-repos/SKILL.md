---
name: scan-repos
description: Scan local repositories and compare with tracked repos
version: 1.0
parameters:
  - name: mode
    type: string
    description: Scan mode (untracked, missing, all)
    default: all
    optional: true
agent: memory-manager
---

# Scan Repositories

This skill scans local repository directories and compares with the memory system.

## Instructions for Agent

### 1. Determine Scan Scope

The scan will check:
- **Windows**: `C:\Users\{user}\repos`
- **WSL/Linux**: `/home/{user}/repos`

On Windows machines, scan both locations to find all repositories.

### 2. Get Current Machine Context

- Machine identifier: `hostname` (lowercase)
- OS: Windows/WSL/Linux

### 3. Call Python Script

Execute the scan_repos.py script:

```bash
cd /path/to/.prototype-plugin
python scripts/scan_repos.py scan-repos \
  --config-repo /path/to/yoshiwatanabe-configurations \
  --mode {mode} \
  --machine {machine}
```

### 4. Parse Results

Expected JSON output:
```json
{
  "untracked": ["temp-repo", "test-project"],
  "missing": ["old-repo"],
  "scan_paths": ["C:\\Users\\twatana\\repos"],
  "total_local": 15,
  "total_tracked": 14
}
```

### 5. Format and Display

Based on mode parameter:

**Mode: untracked**
```
Found 2 untracked repositories:
- temp-repo
- test-project

These repos exist locally but are not in the memory system.
Would you like to add them with /describe-repo?
```

**Mode: missing**
```
Found 1 repository in memory but not found locally:
- old-repo (last seen: 2 weeks ago)

This repo may have been deleted or moved.
```

**Mode: all**
```
Repository Scan Results:

Scanned: C:\Users\twatana\repos
- Total local repositories: 15
- Total tracked in memory: 14

Untracked (2):
- temp-repo
- test-project

Missing (1):
- old-repo

Suggestion: Review untracked repos and decide whether to track or clean up.
```

## Example Usage

**User:** "Scan my repos and show what's not tracked"

**Agent:**
1. Scans C:\Users\{user}\repos and /home/{user}/repos
2. Calls scan_repos.py with mode="untracked"
3. Displays untracked repositories
4. Suggests next actions
