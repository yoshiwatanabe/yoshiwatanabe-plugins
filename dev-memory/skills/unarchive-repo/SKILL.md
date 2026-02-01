---
name: unarchive-repo
description: Restore an archived repository to active queries
version: 1.0
parameters:
  - name: repo_name
    type: string
    description: Repository name or slug to unarchive
    required: true
agent: memory-manager
---

# Unarchive Repository

This skill restores an archived repository so it appears in query results again.

## Instructions for Agent

### 1. Identify Repository

- Get repository name/slug from user parameter
- If user refers to "current repo" or "this repo", extract from git:
  - `git rev-parse --show-toplevel` to get repo path
  - Normalize path to slug format

### 2. Call Python Script

Execute the manage_memory.py script:

```bash
cd /path/to/.prototype-plugin-dev
source venv/bin/activate  # or venv\Scripts\Activate.ps1 on Windows
python scripts/manage_memory.py unarchive-repo \
  --config-repo /path/to/yoshiwatanabe-configurations \
  --repo-name {repo_name}
```

### 3. Handle Result

Parse the JSON output:
```json
{
  "success": true,
  "repo_slug": "revived-project",
  "archived": false,
  "filepath": "domains/dev/memory/repositories/revived-project.md"
}
```

Return confirmation to the user:
```
Repository restored!
- Repository: revived-project
- Status: Now visible in queries
- Synced to remote: Yes
```

If error occurs:
```json
{
  "success": false,
  "error": "Repository 'xyz' not found in memory system"
}
```

Inform user that the repository doesn't exist in the memory system.

## Example Usage

**User:** "unarchive the legacy-api repo, we're using it again"

**Agent:**
1. Identifies repository name: legacy-api
2. Calls manage_memory.py unarchive-repo
3. Confirms repository was restored

**User:** "restore this repo to my active list"

**Agent:**
1. Gets current repository path
2. Calls manage_memory.py unarchive-repo
3. Confirms repository was unarchived
