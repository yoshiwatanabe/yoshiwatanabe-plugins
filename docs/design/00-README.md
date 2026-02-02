# Personal Memory System - Design Documentation

## Overview

This directory contains the complete design for a personal memory and context management system that helps track work across multiple machines, repositories, branches, and worktrees.

## Problem Statement

Managing context across:
- **3 machines:** work-main, work-devbox, personal-pc
- **2 environments per machine:** Windows + WSL (6 total environments)
- **Multiple repositories:** Azure DevOps, GitHub Enterprise, personal GitHub
- **Multiple branches and worktrees** per repository
- **High-level goals and progress** that get lost between sessions

The system provides a "memory bank" to store and query context about:
- What you were working on
- Where (machine, OS, repo, branch)
- What the goals and progress were
- When you last accessed it

## Solution Architecture

### Components

1. **Data Storage (Private Repo):** `yoshiwatanabe-configurations`
   - Single source of truth stored in private GitHub repo
   - Contains memory episodes, repository metadata, machine state
   - Technology-agnostic format (can be used by future AI tools)

2. **Logic/Plugins (Public Repo):** `yoshiwatanabe-plugins`
   - Contains memory management plugin
   - Installed per-user in `.claude/plugins/`
   - Python scripts + Claude Agent Skills + Subagent

3. **Local Clone Strategy:**
   - Single clone per machine at `C:\Users\<user>\repos\yoshiwatanabe-configurations`
   - Both Windows and WSL access same clone
   - Git sync keeps it synchronized with remote

### Key Features

- **Save memory episodes:** Capture session progress with context
- **Query across machines:** Find where you worked on something
- **Repository discovery:** Scan and track repositories
- **Search by description:** Find work by feature name or keywords
- **Repository metadata:** Add descriptions and notes to repos

### Technology Stack

- **Python 3.8+** with venv isolation
- **Claude Code** skills and subagents
- **Git** for synchronization
- **YAML frontmatter** for efficient indexing

## Design Documents

### Core Design
1. **[01-architecture-overview.md](01-architecture-overview.md)**
   - High-level system architecture
   - Data flow diagrams
   - Technology decisions

2. **[02-data-model.md](02-data-model.md)**
   - Memory episode structure (YAML + Markdown)
   - Repository metadata schema
   - Machine state schema
   - Indexing strategy

3. **[03-plugin-structure.md](03-plugin-structure.md)**
   - Plugin directory layout
   - Installation scripts (Windows + Linux)
   - Configuration management
   - Python venv setup

### Implementation Details
4. **[04-skills-definition.md](04-skills-definition.md)**
   - 6 Claude Agent Skills:
     - save-memory
     - describe-repo
     - find-repo
     - scan-repos
     - list-recent-repos
     - search-memory

5. **[05-subagent-definition.md](05-subagent-definition.md)**
   - Memory manager subagent
   - Responsibilities and workflows
   - Error handling
   - Security considerations

6. **[06-python-implementation.md](06-python-implementation.md)**
   - 5 Python modules:
     - manage_memory.py (save, describe)
     - sync_git.py (pull, commit, push)
     - query_memory.py (find, search, list recent)
     - scan_repos.py (discover repos)
     - utils.py (helpers)

### Project Management
7. **[07-implementation-roadmap.md](07-implementation-roadmap.md)**
   - Phase 1: Foundation (MVP)
   - Phase 2: Query and Discovery
   - Phase 3: Polish and Optimization
   - Phase 4: Advanced Features
   - Testing strategy
   - Deployment plan
   - Risk mitigation

## Use Cases

The system supports these key scenarios:

1. **Save session progress**
   - "Hey remember the progress in this session"
   - Captures repo, branch, machine, goals, progress

2. **Add repository metadata**
   - "This repo contains Dynamics packages, needs Core-Platform approval"
   - Adds rich context to repositories

3. **Find repository clones**
   - "Where else do I have clones of this repo?"
   - Shows all machines with this repo

4. **Scan for untracked repos**
   - "Show me repos not tracked by the system"
   - Discovers orphaned or forgotten repos

5. **Recent activity**
   - "Show me 5 repos I worked on recently"
   - Cross-machine activity view

6. **Search by feature**
   - "I worked on Azure key vault isolation, which repo?"
   - Semantic search through memory

## Key Design Decisions

### 1. Separation of Data and Logic
- **Data:** Private repo (yoshiwatanabe-configurations)
- **Logic:** Public repo (yoshiwatanabe-plugins)
- **Benefit:** Data remains technology-agnostic

### 2. Single Local Clone per Machine
- Both Windows and WSL access same clone
- Avoids duplication and sync issues

### 3. Python + venv
- Cross-platform scripting
- Isolated dependencies per environment
- Rich ecosystem for git/YAML/file ops

### 4. Claude Skills + Subagent
- Skills provide user interface
- Subagent isolates memory operations
- Prevents token bloat in main session

### 5. YAML Frontmatter
- Efficient metadata indexing
- Progressive disclosure in AI context
- Human-readable and editable

### 6. Git-based Sync
- Simple, proven technology
- Leverages GitHub infrastructure
- Familiar conflict resolution

### 7. Extensibility
- Config repo can grow beyond dev memory
- Support for cars, finance, etc. in future
- Plugin architecture allows multiple plugins

## Security Considerations

- **Private GitHub repo** for data storage
- **Non-sensitive data only** (no credentials)
- **User accepts risk** of private repo not being perfectly confidential
- Historical context and goals are acceptable to store

## Cross-Platform Support

### Windows
- Python venv: `C:\Users\<user>\.claude\plugins\yoshiwatanabe-memory\venv`
- Config repo: `C:\Users\<user>\repos\yoshiwatanabe-configurations`
- Repos scan: `C:\Users\<user>\repos`

### WSL/Linux
- Python venv: `/home/<user>/.claude/plugins/yoshiwatanabe-memory/venv`
- Config repo: `/mnt/c/Users/<user>/repos/yoshiwatanabe-configurations` (shared)
- Repos scan: `/home/<user>/repos`

## Installation Flow

1. Clone `yoshiwatanabe-configurations` to `C:\Users\<user>\repos\`
2. Clone `yoshiwatanabe-plugins` repo
3. Run `install.sh` (Linux) or `install.ps1` (Windows)
4. Configure plugin: `claude config set yoshiwatanabe-memory.configRepoPath <path>`
5. Use skills: `/save-memory`, `/search-memory`, etc.

## Next Steps

1. **Review design documents** - Ensure all requirements are met
2. **Approve design** - Get sign-off to proceed
3. **Start Phase 1** - Implement MVP (foundation)
4. **Test on devbox** - Verify cross-platform compatibility
5. **Deploy to other machines** - Roll out incrementally
6. **Iterate and improve** - Gather feedback, add features

## Questions for Review

1. Does the architecture meet all use case requirements?
2. Is Python the right choice for scripting?
3. Is the YAML frontmatter approach efficient enough?
4. Should we add indexing earlier (Phase 1 vs Phase 3)?
5. Are there any security concerns with the private GitHub repo approach?
6. Should we support additional categories (cars, finance) in Phase 1 or later?

## Document Status

- **Status:** Draft - Ready for Review
- **Version:** 1.0
- **Date:** 2026-01-31
- **Author:** Claude (with Yoshi Watanabe)

---

For questions or feedback, refer to individual design documents or the implementation roadmap.
