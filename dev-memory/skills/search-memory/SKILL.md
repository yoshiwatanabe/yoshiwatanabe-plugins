---
name: search-memory
description: Search development memory using semantic understanding
version: 2.0
parameters:
  - name: query
    type: string
    description: Natural language search query
    required: true
  - name: limit
    type: number
    description: Maximum results to return
    default: 5
    optional: true
agent: memory-manager
allowed-tools: Glob, Read
user-invocable: true
---

# Search Memory (Semantic)

Search through memory episodes using Claude's semantic understanding, not just keyword matching.

## Instructions for Agent

### 1. Find All Episodes

Get configuration path from `YW_CONFIG_REPO_PATH` environment variable.

Find all episode files:
```
Use Glob tool: $YW_CONFIG_REPO_PATH/domains/dev/memory/episodes/*.md
```

Sort by filename (most recent first) and limit to 50 most recent episodes if there are many.

### 2. Read Episode Frontmatter

For each episode file:
```
Use Read tool: Read first 40 lines (YAML frontmatter + summary)
```

Extract from YAML:
- `id`: Episode ID
- `timestamp`: When created
- `machine`: Which machine
- `os`: Operating system
- `repository.name`: Repository
- `repository.branch`: Git branch
- `repository.commit`: Commit hash (show first 7 chars)
- `summary`: Episode summary
- `keywords`: Keywords list
- `context.tags`: Tags list

### 3. Semantic Analysis

**CRITICAL:** Use semantic understanding, not keyword matching!

Analyze which episodes are relevant to user's query by:
- Understanding **query intent** (what is the user really asking?)
- Considering **synonyms** and related concepts
- Looking at **context** in summary, keywords, and tags
- Weighing **recency** (recent work often more relevant)

**Examples of semantic understanding:**
- Query: "plugin development" → Match: "Claude Code extensions", "marketplace", "skills"
- Query: "authentication" → Match: "OAuth", "login flow", "security tokens", "auth"
- Query: "what did I do last week?" → Match: Recent episodes by timestamp

Don't just grep for exact words - understand meaning!

### 4. Rank Results

Select top {limit} most semantically relevant episodes.

Sort by:
1. **Relevance** to query (primary)
2. **Recency** (secondary tiebreaker)

### 5. Format Output

For each result:

```
Found {count} episodes matching "{query}":

1. {Summary first sentence} ({relative_date})
   Machine: {machine} ({os})
   Repository: {repo_name} ({branch})
   Commit: {first_7_chars_of_commit}

   {Full summary from episode}

   → Why relevant: {Explain semantic connection to query}

2. {Next episode...}
```

**Relative dates:**
- Today → "Today"
- Yesterday → "Yesterday"
- This week → "3 days ago"
- Older → "Jan 15, 2026"

**If no relevant episodes:**
```
No episodes found matching "{query}" semantically.

You have {total_count} episodes. Try:
- Broader terms: "authentication" vs "OAuth2 PKCE flow"
- Different phrasing: "API work" vs "endpoint development"
- /list-recent-repos to see recent activity
```

### 6. Explanation Quality

Always explain WHY each episode matches. Examples:

✅ Good: "Relevant because: Discusses plugin architecture and marketplace setup"
✅ Good: "Relevant because: Authentication work using OAuth, matches your query"
❌ Bad: "Relevant because: Contains keyword 'plugin'"
❌ Bad: "Relevant because: Recent"

## Advantages Over Keyword Search

✅ Understands synonyms (auth = authentication = OAuth)
✅ Contextual (knows "marketplace" relates to "plugins")
✅ Natural queries ("what did I work on?" vs keywords)
✅ Explains relevance (not just shows matches)

## Example Queries

**Broad:**
- "What did I work on this week?"
- "Show me authentication work"

**Specific:**
- "Which repo has OAuth implementation?"
- "When did I work on marketplace plugin?"

**Conceptual:**
- "Security improvements"
- "Cross-platform fixes"
