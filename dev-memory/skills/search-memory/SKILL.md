---
name: search-memory
description: Search memory episodes by feature, work description, or keywords
version: 1.0
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

# Search Memory

This skill searches memory episodes using keywords or feature descriptions.

## Instructions for Agent

### 1. Parse Query

Extract keywords from the user's query:
- Split on spaces
- Lowercase for case-insensitive search
- Identify potential:
  - Feature names (e.g., "auth validator", "key vault isolation")
  - Technologies (e.g., "Azure", "Dynamics")
  - Date references (convert to search terms if possible)

### 2. Call Python Script

Execute the query_memory.py script:

```bash
# Plugin root is current directory when skill executes
source ./venv/bin/activate  # or .envScriptsctivate on Windows
python ./scripts/query_memory.py search-memory \
  --config-repo "$YW_CONFIG_REPO_PATH" \
  --query "{query}" \
  --limit {limit}
```

### 3. Parse Results

Expected JSON output:
```json
[
  {
    "episode_id": "ep-12345abcd",
    "timestamp": "2026-01-31T14:30:00Z",
    "machine": "work-main",
    "os": "windows",
    "repository": "dynamics-solutions",
    "branch": "feature/auth-validator",
    "commit": "abc123def456",
    "summary": "Completed auth validator test implementation",
    "keywords": ["auth", "validator", "test", "dynamics"],
    "tags": ["azure-devops", "testing"]
  },
  ...
]
```

### 4. Format and Display

Present matching episodes:

```
Found 3 memory episodes matching "Azure key vault isolation":

1. Azure Key Vault secret isolation feature (Dec 15, 2025)
   Repository: azure-infra
   Branch: feature/keyvault-isolation
   Commit: abc123d
   Machine: work-main (Windows)

   Completed implementation of key vault secret isolation
   for multi-tenant environments.

2. Key vault configuration update (Dec 10, 2025)
   Repository: azure-infra
   Branch: main
   Commit: def456a
   Machine: work-devbox (WSL)

   Updated key vault access policies to support isolation.

...

Use episode ID to view full details (stored in memory/episodes/).
```

Highlight:
- **Best matches** (all keywords present)
- **Most recent** episodes first
- **Repository and branch** for context
- **Commit hash** for reference

### 5. Provide Context

If results found:
```
Tip: Clone location on {machine}: {path}
     Last commit: {commit_hash}
```

If no results:
```
No memory episodes found matching "{query}".

Try:
- Broader search terms
- Check if work was tracked with /save-memory
- Use /list-recent-repos to browse repositories
```

## Example Usage

**User:** "I worked on Azure key vault isolation, which repo was that?"

**Agent:**
1. Parses keywords: ["azure", "key", "vault", "isolation"]
2. Calls query_memory.py search-memory
3. Returns matching episode with repository, branch, and commit details
4. Provides context for locating the code
