---
name: list-recent-repos
description: List recently worked-on repositories
version: 1.0
parameters:
  - name: count
    type: integer
    description: Number of repositories to show
    default: 5
    optional: true
  - name: filter
    type: string
    description: Filter by machine type (work, personal, all)
    default: all
    optional: true
agent: memory-manager
---

# List Recent Repositories

This skill lists recently worked-on repositories across all machines.

## Instructions for Agent

### 1. Apply Parameters

- **count**: Number of results to return (default: 5)
- **filter**: Machine type filter (work, personal, all)

### 2. Call Python Script

Execute the query_memory.py script:

```bash
# Plugin root is current directory when skill executes
source ./venv/bin/activate  # or .envScriptsctivate on Windows
python ./scripts/query_memory.py list-recent-repos \
  --config-repo "$YW_CONFIG_REPO_PATH" \
  --count {count} \
  --filter {filter}
```

### 3. Parse Results

Expected JSON output:
```json
[
  {
    "name": "dynamics-solutions",
    "description": "Dynamics solution packages...",
    "last_accessed": "2026-01-31T14:30:00Z",
    "last_machine": "work-main",
    "last_os": "windows",
    "clones": [
      {
        "machine": "work-main",
        "os": "windows",
        "path": "C:\\Users\\twatana\\repos\\dynamics-solutions",
        "last_accessed": "2026-01-31T14:30:00Z"
      }
    ],
    "tags": ["azure-devops", "dynamics"]
  },
  ...
]
```

### 4. Format and Display

Present results in a clean list:

```
5 most recently accessed repositories:

1. dynamics-solutions (work-main, Windows - today)
   Dynamics solution packages for the team
   Tags: azure-devops, dynamics

2. personal-blog (personal-pc, WSL - 3 days ago)
   Personal blog built with Hugo
   Tags: hugo, blog

3. azure-infra (work-devbox, Linux - 1 week ago)
   Infrastructure as code for Azure
   Tags: terraform, azure

...

Use /find-repo {name} to see all clones of a repository.
```

Highlight repositories:
- Worked on **today** or **this week**
- Current machine (if applicable)

### 5. Suggest Next Actions

If the user might want to resume work:
```
Suggestion: Use /search-memory to find specific work you did on these repos.
```

## Example Usage

**User:** "Show me 5 repos I worked on recently"

**Agent:**
1. Calls query_memory.py list-recent-repos --count 5
2. Formats results with descriptions and last access info
3. Displays in order of most recent access
