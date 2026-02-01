---
name: archive-repo
description: Archive (hide) an obsolete repository from queries
version: 1.0
parameters:
  - name: repo_name
    type: string
    description: Repository name or slug to archive
    required: true
  - name: reason
    type: string
    description: Optional reason for archiving
    optional: true
agent: memory-manager
---

# Archive Repository

This skill archives an obsolete repository so it won't appear in query results.

## Instructions for Agent

### 1. Identify Repository

- Get repository name/slug from user parameter
- If user refers to "current repo" or "this repo", extract from git:
  - `git rev-parse --show-toplevel` to get repo path
  - Normalize path to slug format

### 2. Collect Context

- **Reason**: If user provides context, capture why the repo is being archived
  - Examples: "no longer maintained", "deprecated", "merged into another repo"
- Confirm with user if not explicitly stated

### 3. Call Python Script

Execute the manage_memory.py script:

```bash
cd "${CLAUDE_PLUGIN_ROOT}"

# Detect Python command (python3 on Linux, python on Windows)
PYTHON_CMD=$(command -v python3 || command -v python)

# Try to use venv if available, create if needed, skip if venv creation fails
if [ -d "venv" ]; then
  # Activate venv (cross-platform)
  if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
  elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
  fi
elif $PYTHON_CMD -m venv venv 2>/dev/null; then
  echo "Setting up Python environment (first time)..."
  if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
  elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
  fi
  pip install -r requirements.txt
else
  echo "Note: Using system Python (venv creation not available)"
fi
source venv/bin/activate  # or venv\Scripts\Activate.ps1 on Windows
# Use python3 on Linux/WSL, python on Windows
$PYTHON_CMD scripts/manage_memory.py archive-repo \
  --config-repo "$YW_CONFIG_REPO_PATH" \
  --repo-name {repo_name} \
  --reason "{reason}"
```

### 4. Handle Result

Parse the JSON output:
```json
{
  "success": true,
  "repo_slug": "old-project",
  "archived": true,
  "filepath": "domains/dev/memory/repositories/old-project.md"
}
```

Return confirmation to the user:
```
Repository archived!
- Repository: old-project
- Reason: {reason if provided}
- Status: Will no longer appear in queries
- Note: Use /unarchive-repo to restore visibility
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

**User:** "archive the old-service repo, it's been deprecated"

**Agent:**
1. Identifies repository name: old-service
2. Extracts reason: "deprecated"
3. Calls manage_memory.py archive-repo
4. Confirms repository was archived

**User:** "hide this repo from my queries"

**Agent:**
1. Gets current repository path
2. Asks user for archival reason
3. Calls manage_memory.py archive-repo
4. Confirms repository was archived
