---
name: find-repo
description: Find clones of a repository across all machines
version: 1.0
parameters:
  - name: repo_name
    type: string
    description: Repository name or slug to search for
    optional: true
agent: memory-manager
---

# Find Repository

This skill finds all clones of a repository across all machines and environments.

## Instructions for Agent

### 1. Identify Target Repository

- If `repo_name` parameter not provided:
  - Use current repository: `git rev-parse --show-toplevel`
  - Extract repo name from path
- If `repo_name` provided:
  - Normalize to repo slug (basename)

### 2. Call Python Script

Execute the query_memory.py script:

```bash
cd /path/to/.prototype-plugin
python scripts/query_memory.py find-repo \
  --config-repo /path/to/yoshiwatanabe-configurations \
  --repo-name {repo_name}
```

### 3. Parse Results

Expected JSON output:
```json
{
  "repository": "dynamics-solutions",
  "description": "Dynamics solution packages...",
  "clones": [
    {
      "machine": "work-main",
      "os": "windows",
      "path": "C:\\Users\\twatana\\repos\\dynamics-solutions",
      "last_accessed": "2026-01-31T14:30:00Z"
    },
    {
      "machine": "work-devbox",
      "os": "wsl",
      "path": "/home/twatana/repos/dynamics-solutions",
      "last_accessed": "2026-01-15T10:00:00Z"
    }
  ],
  "tags": ["azure-devops", "dynamics"],
  "found": true
}
```

### 4. Format and Display

Present results in a user-friendly format:

```
Repository: dynamics-solutions
Description: Dynamics solution packages...

Found 2 clones:

1. work-main (Windows)
   Path: C:\Users\twatana\repos\dynamics-solutions
   Last accessed: Jan 31, 2026

2. work-devbox (WSL)
   Path: /home/twatana/repos/dynamics-solutions
   Last accessed: Jan 15, 2026

Tags: azure-devops, dynamics
```

If `found: false`:
```
Repository '{repo_name}' not found in memory system.

This repository has not been tracked yet. Use /describe-repo to add it.
```

## Example Usage

**User:** "Hey where else do I have clones of this repository?"

**Agent:**
1. Identifies current repository
2. Calls query_memory.py find-repo
3. Formats and displays clone locations across machines
