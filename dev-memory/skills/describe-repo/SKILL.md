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

Get the configuration repository path from environment:
- Read `YW_CONFIG_REPO_PATH` environment variable (required)
- Plugin is installed at `~/.claude/plugins/yoshiwatanabe-dev/`

Execute the manage_memory.py script:

```bash
cd ~/.claude/plugins/yoshiwatanabe-dev
source venv/bin/activate  # or venv\Scripts\activate on Windows
python scripts/manage_memory.py describe-repo \
  --config-repo "$YW_CONFIG_REPO_PATH" \
  --repo-path {repo_path} \
  --description "{description}" \
  --tags "{tags}" \
  --machine {machine} \
  --os {os}
```

**Note:** If `YW_CONFIG_REPO_PATH` is not set, return an error telling the user to configure it in `~/.claude/settings.json`

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
