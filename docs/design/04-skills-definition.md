# Skills Definition

## Overview

Each skill is a `.md` file with YAML frontmatter that defines:
- Skill metadata (name, description, parameters)
- Instructions for the subagent
- Integration with Python scripts

## Skill 1: save-memory

**File:** `skills/save-memory.md`

```markdown
---
name: save-memory
description: Save current session progress and context to memory
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

# Save Memory Skill

This skill saves the current session's progress and context to the personal memory system.

## Instructions for Agent

1. **Collect Session Context:**
   - Identify current working directory
   - Detect repository (if in a git repo)
   - Determine branch and latest commit
   - Detect worktree (if applicable)
   - Identify machine and OS environment

2. **Generate Summary:**
   - Analyze recent conversation history
   - Extract goals, activities, and progress
   - Identify keywords and topics
   - Determine next steps (if mentioned)
   - Use specified detail_level parameter

3. **Call Python Script:**
   ```bash
   python scripts/manage_memory.py save \
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

4. **Confirm Success:**
   - Report episode ID
   - Report sync status (pushed to remote)
   - Suggest related operations (if applicable)

## Example Usage

User: "hey remember the progress in this session"
Agent: Saves session context and returns confirmation with episode ID.
```

## Skill 2: describe-repo

**File:** `skills/describe-repo.md`

```markdown
---
name: describe-repo
description: Add or update repository metadata and description
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

# Describe Repository Skill

This skill adds or updates metadata for the current repository.

## Instructions for Agent

1. **Identify Repository:**
   - Detect current repository path
   - Extract repository name and remote URL
   - Determine category (work/personal based on remote)

2. **Collect Metadata:**
   - Parse user's description
   - Extract team, approval process, notes
   - Add user-provided tags
   - Record current machine and OS

3. **Call Python Script:**
   ```bash
   python scripts/manage_memory.py describe-repo \
     --repo-path {repo_path} \
     --description "{description}" \
     --tags "{tags}" \
     --machine {machine} \
     --os {os}
   ```

4. **Confirm Success:**
   - Report repository slug
   - Show updated metadata
   - Suggest related operations

## Example Usage

User: "Hey, this repo contains Dynamics solution packages. We need Core-Platform approval for PRs."
Agent: Adds metadata to repository and confirms.
```

## Skill 3: find-repo

**File:** `skills/find-repo.md`

```markdown
---
name: find-repo
description: Find clones of a repository across all machines
parameters:
  - name: repo_name
    type: string
    description: Repository name or slug to search for
    optional: true
agent: memory-manager
---

# Find Repository Skill

This skill finds all clones of a repository across all machines and environments.

## Instructions for Agent

1. **Identify Target Repository:**
   - If repo_name not provided, use current repository
   - Normalize repository name/slug

2. **Call Python Script:**
   ```bash
   python scripts/query_memory.py find-repo \
     --repo-name {repo_name}
   ```

3. **Format Results:**
   - List all machines where repo is cloned
   - Show OS environment (Windows/WSL)
   - Display last accessed date
   - Show recent activity summary

4. **Provide Context:**
   - Highlight current machine
   - Suggest next steps if applicable

## Example Usage

User: "Hey where else do I have clones of this repository?"
Agent: Returns list of machines with clones and recent activity.
```

## Skill 4: scan-repos

**File:** `skills/scan-repos.md`

```markdown
---
name: scan-repos
description: Scan local repositories and compare with tracked repos
parameters:
  - name: mode
    type: string
    description: Scan mode (untracked, missing, all)
    default: all
    optional: true
agent: memory-manager
---

# Scan Repositories Skill

This skill scans local repository directories and compares with the memory system.

## Instructions for Agent

1. **Determine Scan Locations:**
   - Windows: `C:\Users\{user}\repos`
   - WSL: `/home/{user}/repos`
   - Scan both if on Windows machine

2. **Call Python Script:**
   ```bash
   python scripts/scan_repos.py scan-repos \
     --mode {mode} \
     --machine {machine}
   ```

3. **Format Results Based on Mode:**

   **Mode: untracked**
   - List repos found locally but not in memory system
   - Show size, creation date
   - Suggest adding to memory or cleaning up

   **Mode: missing**
   - List repos in memory system but not found locally
   - Show last accessed date
   - Suggest cleanup or re-cloning

   **Mode: all**
   - Show both untracked and missing
   - Provide summary statistics

4. **Suggest Actions:**
   - Offer to add untracked repos to memory
   - Offer to clean up missing entries

## Example Usage

User: "Scan my repos and show what's not tracked"
Agent: Returns list of untracked repositories.
```

## Skill 5: list-recent-repos

**File:** `skills/list-recent-repos.md`

```markdown
---
name: list-recent-repos
description: List recently worked-on repositories
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

# List Recent Repositories Skill

This skill lists recently worked-on repositories across all machines.

## Instructions for Agent

1. **Apply Filters:**
   - Count: number of results to return
   - Filter: work/personal/all machines

2. **Call Python Script:**
   ```bash
   python scripts/query_memory.py list-recent-repos \
     --count {count} \
     --filter {filter}
   ```

3. **Format Results:**
   - Repository name and description
   - Machine and OS
   - Branch and worktree (if applicable)
   - Last accessed date
   - Brief activity summary
   - Tags

4. **Provide Context:**
   - Highlight repos worked on today/this week
   - Suggest resuming work if applicable

## Example Usage

User: "Show me 5 repos I worked on recently"
Agent: Returns 5 most recently accessed repositories with context.
```

## Skill 6: search-memory

**File:** `skills/search-memory.md`

```markdown
---
name: search-memory
description: Search memory episodes by feature, work description, or keywords
parameters:
  - name: query
    type: string
    description: Search query (keywords, feature name, etc.)
    required: true
  - name: limit
    type: integer
    description: Maximum number of results
    default: 10
    optional: true
agent: memory-manager
---

# Search Memory Skill

This skill searches memory episodes using keywords or feature descriptions.

## Instructions for Agent

1. **Parse Query:**
   - Extract keywords from user's query
   - Identify potential dates, repo names, tags

2. **Call Python Script:**
   ```bash
   python scripts/query_memory.py search-memory \
     --query "{query}" \
     --limit {limit}
   ```

3. **Format Results:**
   - Episode summary
   - Repository, branch, commit
   - Machine and OS
   - Date
   - Relevant excerpt from episode content

4. **Provide Context:**
   - Highlight best matches
   - Suggest related episodes if applicable
   - Offer to show full episode details

## Example Usage

User: "I worked on Azure key vault isolation, which repo was that?"
Agent: Returns matching episode with repository, branch, and commit details.
```

## Skill Invocation Pattern

All skills follow this pattern:

1. **User invokes skill:** `/save-memory` or natural language
2. **Main session calls skill:** Skill definition loaded
3. **Skill spawns subagent:** memory-manager agent
4. **Subagent executes:** Calls Python scripts, processes results
5. **Subagent returns:** Formatted results back to main session
6. **Main session displays:** Results shown to user

## Error Handling

All skills should handle common errors:
- Config repo not found/not configured
- Git operation failures
- Python script errors
- Invalid parameters

Error messages should be clear and suggest remediation steps.
