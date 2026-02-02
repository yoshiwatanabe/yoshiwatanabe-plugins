# Unique Repository Naming Convention

## Overview

Repository metadata files use a **machine + path based naming scheme** to ensure each working directory gets its own metadata file, preventing collisions and enabling separate tracking of different work contexts.

## Naming Format

```
{repo_name}-{hash}.md
```

Where:
- `{repo_name}`: Directory name of the repository
- `{hash}`: 8-character SHA256 hash of `machine:path`

### Examples

```
Machine A: C:\users\twatana\repos\xyz
→ xyz-a1b2c3d4.md

Machine B: C:\users\twatana\repos\xyz
→ xyz-e5f6g7h8.md

Machine A: C:\users\twatana\repos\xyz-test
→ xyz-test-f9g0h1i2.md

Machine A: D:\projects\xyz
→ xyz-9a8b7c6d.md
```

## Problem Statement

The original implementation had a critical flaw in how repository metadata files were named:

### Original Approach (v1.0)

```python
def normalize_repo_slug(repo_path):
    return Path(repo_path).name  # Just the directory name
```

This caused **collisions** in several scenarios:

1. **Different repositories with the same directory name**
   ```
   C:\work\api     → api.md
   C:\personal\api → api.md  ❌ COLLISION
   ```

2. **Same repository cloned in multiple locations on same machine**
   ```
   C:\repos\myproject      → myproject.md
   D:\backup\myproject     → myproject.md  ❌ COLLISION
   ```

3. **Same path on different machines with different purposes**
   ```
   Machine A: C:\repos\xyz (implementation work)
   Machine B: C:\repos\xyz (testing work)
   Both → xyz.md  ❌ COLLISION (wanted separate tracking)
   ```

### v1.0 Design Intent vs. Reality

The v1.0 design intended:
- One metadata file per repository (identified by remote URL)
- Track multiple clone locations in a `clones` array

However, this didn't match the actual use case:
- Users work in different directories for different purposes (feature branches, testing, implementation)
- Each working directory represents a **separate work context** that should be tracked independently
- Same repository cloned multiple times should have separate metadata

## Solution: Machine + Path Based Hashing

### Algorithm

```python
def normalize_repo_slug(repo_path, machine):
    """
    Generate unique slug based on machine + local path.

    Ensures each working directory on each machine gets its own
    metadata file.
    """
    import hashlib
    from pathlib import Path

    repo_name = Path(repo_path).name

    # Normalize path for consistent hashing
    full_path = str(Path(repo_path).resolve()).lower().replace('\\', '/')

    # Generate unique key combining machine and path
    unique_key = f"{machine.lower()}:{full_path}"

    # Generate short hash (8 chars = 4+ billion possibilities)
    path_hash = hashlib.sha256(unique_key.encode('utf-8')).hexdigest()[:8]

    return f"{repo_name}-{path_hash}"
```

### Why This Works

✅ **Each local directory gets its own metadata file**
- Different paths → different hashes → different files

✅ **Different machines with same path → different files**
- Machine identifier is part of hash

✅ **Same directory name in different locations → different files**
- Full path is part of hash

✅ **Stable and predictable**
- Same machine + path always produces same hash

✅ **Human-readable**
- Filename includes repository name for easy identification

## Metadata Structure Changes

### v1.0 Structure (Old)

```yaml
---
type: repository-metadata
version: '1.0'
repository:
  name: yoshiwatanabe-configurations
  slug: yoshiwatanabe-configurations
  remote: https://github.com/user/repo.git
clones:
  - machine: machineA
    os: windows
    path: C:\repos\project
    last_accessed: '2026-01-01T00:00:00Z'
  - machine: machineB
    os: linux
    path: /home/user/repos/project
    last_accessed: '2026-01-02T00:00:00Z'
description: Repository description
tags: [tag1, tag2]
---
```

### v2.0 Structure (New)

```yaml
---
type: repository-metadata
version: '2.0'
repository:
  name: yoshiwatanabe-configurations
  slug: yoshiwatanabe-configurations-a1b2c3d4
  remote: https://github.com/user/repo.git
location:
  machine: machineA
  os: windows
  path: C:\repos\project
  last_accessed: '2026-01-01T00:00:00Z'
description: Repository description
tags: [tag1, tag2]
---
```

### Key Changes

1. **Version**: `1.0` → `2.0`
2. **Removed**: `clones` array (no longer needed)
3. **Added**: `location` object (single location per file)
4. **Updated**: `slug` field now includes hash

## Migration

### Migration Script

Use `migrate_repo_files.py` to convert existing files:

```bash
# Dry run (shows what would happen)
python migrate_repo_files.py --config-repo /path/to/config

# Execute migration
python migrate_repo_files.py --config-repo /path/to/config --execute
```

### Migration Process

For each v1.0 repository file:

1. **Read** the old file and parse frontmatter
2. **Extract** the `clones` array
3. **Create** a new file for each clone with hash-based naming
4. **Convert** frontmatter from v1.0 to v2.0 format
5. **Backup** the old file to `.migration_backup/`
6. **Delete** the old file

### Example Migration

**Before**:
```
repositories/
  CRM.Omnichannel.md  (contains 2 clones)
```

**After**:
```
repositories/
  CRM.Omnichannel-a1b2c3d4.md      (clone 1: machineA)
  CRM.Omnichannel-e5f6g7h8.md      (clone 2: machineB)
  .migration_backup/
    CRM.Omnichannel.md             (backup)
```

## Use Cases Supported

### 1. Multiple Work Contexts on Same Machine

```
C:\repos\myproject           (main development)
C:\repos\myproject-testing   (testing branch)
D:\backup\myproject          (backup clone)
```

Each gets its own metadata file with separate tracking.

### 2. Same Repository Across Multiple Machines

```
Machine A: C:\repos\xyz  (implementation work)
Machine B: C:\repos\xyz  (testing work)
Machine C: /home/user/repos/xyz  (Linux development)
```

Each machine + path combination gets its own file, enabling separate tracking of work context.

### 3. Different Repositories with Same Name

```
C:\work\api          (work project)
C:\personal\api      (personal project)
```

Different paths → different hashes → no collision.

## Trade-offs

### Benefits
- ✅ No collisions possible
- ✅ Each work context tracked independently
- ✅ Stable and predictable naming
- ✅ Human-readable filenames

### Considerations
- ⚠️ Moving a repository to a new path creates a new metadata file (new hash)
- ⚠️ Renaming a machine requires migration
- ⚠️ Cannot track "same logical repository" across multiple locations (design choice)

## Backwards Compatibility

The migration script ensures smooth transition:
- Old v1.0 files are backed up
- Each clone becomes a separate v2.0 file
- No data loss
- Can be run as dry-run first to preview changes

## Related Files

- `dev-memory/scripts/utils.py` - `normalize_repo_slug()` implementation
- `dev-memory/scripts/manage_memory.py` - Uses new slug generation
- `dev-memory/scripts/scan_repos.py` - Updated for new naming scheme
- `dev-memory/scripts/migrate_repo_files.py` - Migration script
