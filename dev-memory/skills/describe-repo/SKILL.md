---
name: describe-repo
description: Add or update repository metadata and description
version: 1.0
parameters:
  - name: description
    type: string
    description: Description of the repository
    required: true
  - name: tags
    type: array
    description: Tags for categorizing the repository
    optional: true
agent: memory-manager
---

# Describe Repository

This skill adds or updates metadata for the current repository.

## Instructions for Agent

### 1. Identify Repository

- Detect current repository path: `git rev-parse --show-toplevel`
- Extract repository name from path
- Get remote URL: `git remote get-url origin`
- Determine category (work/personal) based on remote URL:
  - Contains "dev.azure.com" or company domain → work
  - Contains "github.com/yoshiwatanabe" → personal

### 2. Collect Metadata

From user's description, extract:
- **Main description**: What the repository contains/does
- **Team information**: If mentioned
- **Approval process**: If mentioned (e.g., "needs Core-Platform approval")
- **Special notes**: Any important context
- **Tags**: From user parameter or inferred from description

Get current machine and OS context:
- Machine: `hostname` (lowercase)
- OS: Windows/WSL/Linux

### 3. Call Python Script

**Step 1: Find plugin directory**
```bash
PLUGIN_DIR=$(find ~/.claude/plugins/cache -type d -path "*/yoshiwatanabe-plugins/yoshiwatanabe-dev/*/scripts" 2>/dev/null | head -1 | xargs dirname)
```

If `PLUGIN_DIR` is empty, return error: "Plugin installation not found. Try reinstalling with /plugin install yoshiwatanabe-dev@yoshiwatanabe-plugins"

**Step 2: Get configuration path**
- Read `YW_CONFIG_REPO_PATH` environment variable (required)
- If not set, return error: "Please set YW_CONFIG_REPO_PATH in ~/.claude/settings.json. See installation guide for WSL path requirements."

**Step 3: Execute the script**
```bash
cd "$PLUGIN_DIR"
source venv/bin/activate
python scripts/manage_memory.py describe-repo \
  --config-repo "$YW_CONFIG_REPO_PATH" \
  --repo-path {repo_path} \
  --description "{description}" \
  --tags "{tags}" \
  --machine {machine} \
  --os {os}
```

### 4. Handle Result

Parse the JSON output:
```json
{
  "success": true,
  "repo_slug": "dynamics-solutions",
  "filepath": "memory/repositories/dynamics-solutions.md"
}
```

Return confirmation to the user:
```
Repository metadata updated!
- Repository: dynamics-solutions
- Description: [user's description]
- Tags: [tags if any]
- Synced to remote: Yes
```

## Example Usage

**User:** "Hey, this repo contains Dynamics solution packages. We need Core-Platform approval for PRs."

**Agent:**
1. Identifies current repository
2. Extracts key information from description
3. Calls manage_memory.py describe-repo
4. Confirms metadata was saved
