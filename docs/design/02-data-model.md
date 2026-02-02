# Data Model

## Memory Episode Structure

Each memory episode is stored as a Claude Agent Skill (`.md` file) with YAML frontmatter.

### File Location
```
yoshiwatanabe-configurations/memory/episodes/
├── 2026-01-31_work-main_windows_repo-abc_episode-001.md
├── 2026-01-31_work-main_wsl_repo-xyz_episode-002.md
└── ...
```

### File Naming Convention
```
{date}_{machine}_{os}_{repo-slug}_{episode-id}.md
```

Example: `2026-01-31_work-main_windows_dynamics-solutions_ep-12345.md`

### YAML Frontmatter Schema

```yaml
---
type: memory-episode
version: 1.0
id: ep-12345-abcd-1234
timestamp: 2026-01-31T14:30:00Z
machine: work-main
os: windows
repository:
  name: dynamics-solutions
  path: C:\Users\twatana\repos\dynamics-solutions
  remote: https://dev.azure.com/contoso/dynamics-solutions.git
  branch: feature/auth-validator
  worktree: C:\Users\twatana\repos\dynamics-solutions-auth
  commit: abc123def456
context:
  session_duration_minutes: 45
  detail_level: normal
  tags:
    - azure-devops
    - dynamics
    - authentication
    - testing
summary: "Completed auth validator test implementation for Dynamics solutions"
keywords:
  - auth validator
  - authentication
  - test
  - dynamics
goals:
  - Implement auth validator tests
  - Update test documentation
progress:
  - Created AuthValidatorTests.cs
  - Added 5 test cases
  - Fixed token validation logic
  - Pending: Core-Platform PR approval
next_steps:
  - Submit PR to Core-Platform team
  - Address review feedback
---

# Session Progress: Auth Validator Tests

## Summary
Completed implementation of authentication validator tests for the Dynamics solutions repository. Added comprehensive test coverage for token validation scenarios.

## Work Done
1. Created `AuthValidatorTests.cs` with 5 test cases
2. Fixed token validation logic in `AuthValidator.cs`
3. Updated test documentation in README

## Challenges
- Token expiration handling required careful edge case testing
- Core-Platform team approval workflow needs clarification

## Next Steps
- Submit PR to Core-Platform team
- Address review feedback
- Monitor for approval

## Notes
- This repo requires Core-Platform approval for all PRs
- Team uses Azure DevOps for source control
```

## Repository Metadata Structure

### File Location
```
yoshiwatanabe-configurations/memory/repositories/
├── dynamics-solutions.md
├── azure-infra.md
└── ...
```

### File Naming Convention
```
{repo-slug}.md
```

### YAML Frontmatter Schema

```yaml
---
type: repository-metadata
version: 1.0
repository:
  name: dynamics-solutions
  slug: dynamics-solutions
  remote: https://dev.azure.com/contoso/dynamics-solutions.git
  category: work
description: "Contains all Dynamics solution packages for the team. Requires Core-Platform approval for PRs."
team: dynamics-team
approval_process: "Core-Platform team review required"
tags:
  - azure-devops
  - dynamics
  - enterprise
clones:
  - machine: work-main
    os: windows
    path: C:\Users\twatana\repos\dynamics-solutions
    last_accessed: 2026-01-31T14:30:00Z
  - machine: work-devbox
    os: wsl
    path: /home/twatana/repos/dynamics-solutions
    last_accessed: 2026-01-15T10:00:00Z
notes: |
  - Always submit PRs with detailed descriptions
  - Core-Platform team typically reviews within 2 days
  - Use conventional commit messages
---

# Repository: dynamics-solutions

## Purpose
Contains all Dynamics solution packages used by the team.

## Approval Process
All PRs require Core-Platform team approval.

## Additional Context
(Extended notes and documentation about this repository)
```

## Machine State Structure

### File Location
```
yoshiwatanabe-configurations/memory/machines/
├── work-main.md
├── work-devbox.md
├── personal-pc.md
```

### YAML Frontmatter Schema

```yaml
---
type: machine-state
version: 1.0
machine:
  id: work-main
  hostname: DESKTOP-ABC123
  type: work
environments:
  - os: windows
    user: C:\Users\twatana
    repos_path: C:\Users\twatana\repos
    last_sync: 2026-01-31T14:30:00Z
  - os: wsl
    user: /home/twatana
    repos_path: /home/twatana/repos
    last_sync: 2026-01-30T09:00:00Z
active_repositories:
  - dynamics-solutions
  - azure-infra
  - personal-config
notes: |
  - Primary work machine
  - Windows 11 + WSL2 Ubuntu 22.04
---

# Machine: work-main

## Configuration
Primary work machine with Windows and WSL environments.

## Active Projects
(List of currently active projects on this machine)
```

## Index Structure (Optional)

For faster queries, maintain index files:

### File Location
```
yoshiwatanabe-configurations/memory/index/
├── by-repository.json
├── by-machine.json
├── by-keyword.json
└── by-date.json
```

### Example: `by-repository.json`
```json
{
  "dynamics-solutions": [
    "2026-01-31_work-main_windows_dynamics-solutions_ep-12345.md",
    "2026-01-15_work-devbox_wsl_dynamics-solutions_ep-12340.md"
  ],
  "azure-infra": [
    "2026-01-28_work-main_windows_azure-infra_ep-12343.md"
  ]
}
```

## Conceptual Model: Configuration vs Memory

### Configuration (Current State)
- Repository metadata (latest)
- Machine state (latest)
- Current active projects

### Memory (Historical Context)
- Memory episodes (append-only, with lifecycle)
- Historical activity
- Older episodes can be archived/pruned

### Relationship
- Configuration = Latest snapshot derived from memory
- Memory = Historical record that led to current configuration

**Implementation:**
- Store both explicitly for clarity
- Repository metadata includes `last_accessed` (configuration)
- Memory episodes provide historical context (memory)
- Queries can target either or both
