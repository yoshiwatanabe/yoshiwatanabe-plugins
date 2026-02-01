---
name: save-memory
description: Save current session progress and context to memory
version: 1.0
parameters:
  - name: detail_level
    type: string
    description: Level of detail for summary (brief, normal, detailed)
    default: normal
    optional: true
  - name: tags
    type: array
    description: Additional tags for this memory episode
    optional: true
agent: memory-manager
---

# Save Memory

This skill saves the current session's progress and context to the personal memory system.

## Instructions for Agent

### 1. Collect Session Context

Gather the following information:
- **Current working directory**: Use `pwd` or `Get-Location`
- **Repository details** (if in a git repo):
  - Repository root: `git rev-parse --show-toplevel`
  - Current branch: `git branch --show-current`
  - Latest commit: `git rev-parse HEAD`
  - Worktree (if applicable): check if cwd is different from repo root
- **Machine identifier**: `hostname` (lowercase)
- **OS environment**:
  - Windows: `$env:OS` contains "Windows"
  - WSL: check `/proc/version` for "microsoft"
  - Linux: `uname -s`

### 2. Generate Summary

Analyze the recent conversation history to extract:
- **Goals**: What was the user trying to accomplish?
- **Activities**: What work was performed?
- **Progress**: What was completed?
- **Next steps**: What remains to be done?
- **Keywords**: Important terms, technologies, features
- **Tags**: Categorize the work (from user parameter or inferred)

Use the specified `detail_level` parameter (or default to "normal").

### 3. Call Python Script

Execute the manage_memory.py script:

```bash
cd ~/.claude/plugins/yoshiwatanabe-dev
source venv/bin/activate  # or venvScriptsctivate on Windows
python scripts/manage_memory.py save \
  --config-repo "$YW_CONFIG_REPO_PATH" \
  --detail-level {detail_level} \
  --repo-path {repo_path} \
  --branch {branch} \
  --commit {commit} \
  --machine {machine} \
  --os {os} \
  --summary "{summary}" \
  --keywords "{keywords}" \
  --tags "{tags}"
```

**Note**: Adjust paths based on Windows vs Linux/WSL:
- Windows: Use `python` and backslash paths
- Linux/WSL: Use `python3` and forward slash paths

### 4. Handle Result

Parse the JSON output:
```json
{
  "success": true,
  "episode_id": "ep-12345abcd",
  "filepath": "memory/episodes/2026-01-31_work-main_windows_repo-name_ep-12345.md",
  "synced": true
}
```

Return a concise confirmation to the user:
```
Memory saved successfully!
- Episode ID: ep-12345abcd
- Location: memory/episodes/...
- Synced to remote: Yes
```

### 5. Error Handling

If the script fails:
- Display the error message clearly
- Suggest remediation steps (e.g., check git repo, verify paths)
- Do not retry automatically

## Example Usage

**User:** "hey remember the progress in this session"

**Agent:**
1. Collects context (repo, branch, machine, OS)
2. Generates summary from conversation
3. Calls manage_memory.py script
4. Returns confirmation with episode ID
