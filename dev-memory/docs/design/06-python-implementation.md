# Python Scripts Implementation

## Overview

Python scripts provide the core logic for memory operations. They are designed to be:
- Cross-platform (Windows + Linux)
- CLI-friendly (can be called from shell)
- Testable (unit tests possible)
- Modular (separate concerns)

## Module Structure

### 1. `manage_memory.py` - Core Memory Operations

```python
#!/usr/bin/env python3
"""
Core memory operations: save, update, archive episodes.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import yaml
from sync_git import SyncGit
from utils import generate_episode_id, normalize_repo_slug, get_machine_id

class ManageMemory:
    def __init__(self, config_repo_path):
        self.config_repo = Path(config_repo_path)
        self.memory_dir = self.config_repo / "memory"
        self.episodes_dir = self.memory_dir / "episodes"
        self.repos_dir = self.memory_dir / "repositories"
        self.git_sync = SyncGit(self.config_repo)

    def save_episode(self, **kwargs):
        """
        Save a memory episode.

        Args:
            detail_level: str - brief, normal, detailed
            repo_path: str - path to repository
            branch: str - git branch
            commit: str - git commit hash
            machine: str - machine identifier
            os: str - operating system (windows, linux)
            summary: str - session summary
            keywords: str - comma-separated keywords
            tags: str - comma-separated tags
            worktree: str - worktree path (optional)
        """
        # Pull latest from remote
        self.git_sync.pull()

        # Generate episode metadata
        episode_id = generate_episode_id()
        timestamp = datetime.utcnow().isoformat() + "Z"
        repo_slug = normalize_repo_slug(kwargs["repo_path"])

        # Build filename
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        filename = f"{date_str}_{kwargs['machine']}_{kwargs['os']}_{repo_slug}_{episode_id}.md"
        filepath = self.episodes_dir / filename

        # Build YAML frontmatter
        frontmatter = {
            "type": "memory-episode",
            "version": "1.0",
            "id": episode_id,
            "timestamp": timestamp,
            "machine": kwargs["machine"],
            "os": kwargs["os"],
            "repository": {
                "name": repo_slug,
                "path": kwargs["repo_path"],
                "remote": self._get_remote_url(kwargs["repo_path"]),
                "branch": kwargs["branch"],
                "commit": kwargs["commit"],
            },
            "context": {
                "detail_level": kwargs["detail_level"],
                "tags": kwargs.get("tags", "").split(",") if kwargs.get("tags") else [],
            },
            "summary": kwargs["summary"],
            "keywords": kwargs.get("keywords", "").split(",") if kwargs.get("keywords") else [],
        }

        if kwargs.get("worktree"):
            frontmatter["repository"]["worktree"] = kwargs["worktree"]

        # Write episode file
        content = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n\n"
        content += f"# Memory Episode: {kwargs['summary']}\n\n"
        content += "## Context\n\n"
        content += f"- **Machine:** {kwargs['machine']}\n"
        content += f"- **OS:** {kwargs['os']}\n"
        content += f"- **Repository:** {repo_slug}\n"
        content += f"- **Branch:** {kwargs['branch']}\n"
        content += f"- **Commit:** {kwargs['commit']}\n\n"

        filepath.write_text(content, encoding="utf-8")

        # Update repository metadata
        self._update_repo_metadata(repo_slug, kwargs)

        # Commit and push
        self.git_sync.commit_and_push(
            files=[str(filepath.relative_to(self.config_repo))],
            message=f"Add memory episode: {kwargs['summary'][:50]}"
        )

        # Return result
        return {
            "success": True,
            "episode_id": episode_id,
            "filepath": str(filepath.relative_to(self.config_repo)),
            "synced": True,
        }

    def describe_repo(self, **kwargs):
        """
        Add or update repository metadata.

        Args:
            repo_path: str - path to repository
            description: str - repository description
            tags: str - comma-separated tags
            machine: str - current machine
            os: str - current OS
        """
        self.git_sync.pull()

        repo_slug = normalize_repo_slug(kwargs["repo_path"])
        filepath = self.repos_dir / f"{repo_slug}.md"

        # Load existing metadata if present
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
            else:
                frontmatter = {}
        else:
            frontmatter = {
                "type": "repository-metadata",
                "version": "1.0",
                "repository": {
                    "name": repo_slug,
                    "slug": repo_slug,
                    "remote": self._get_remote_url(kwargs["repo_path"]),
                },
                "clones": [],
            }

        # Update metadata
        frontmatter["description"] = kwargs["description"]
        frontmatter["tags"] = kwargs.get("tags", "").split(",") if kwargs.get("tags") else []

        # Update or add clone info
        clone_info = {
            "machine": kwargs["machine"],
            "os": kwargs["os"],
            "path": kwargs["repo_path"],
            "last_accessed": datetime.utcnow().isoformat() + "Z",
        }
        clones = frontmatter.get("clones", [])
        updated = False
        for clone in clones:
            if clone["machine"] == kwargs["machine"] and clone["os"] == kwargs["os"]:
                clone.update(clone_info)
                updated = True
                break
        if not updated:
            clones.append(clone_info)
        frontmatter["clones"] = clones

        # Write file
        content = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n\n"
        content += f"# Repository: {repo_slug}\n\n"
        content += f"## Description\n{kwargs['description']}\n\n"

        filepath.write_text(content, encoding="utf-8")

        # Commit and push
        self.git_sync.commit_and_push(
            files=[str(filepath.relative_to(self.config_repo))],
            message=f"Update repository metadata: {repo_slug}"
        )

        return {
            "success": True,
            "repo_slug": repo_slug,
            "filepath": str(filepath.relative_to(self.config_repo)),
        }

    def _get_remote_url(self, repo_path):
        """Get git remote URL for a repository."""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "-C", repo_path, "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _update_repo_metadata(self, repo_slug, context):
        """Update repository metadata with latest access time."""
        filepath = self.repos_dir / f"{repo_slug}.md"

        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])

                # Update last_accessed for matching clone
                for clone in frontmatter.get("clones", []):
                    if clone["machine"] == context["machine"] and clone["os"] == context["os"]:
                        clone["last_accessed"] = datetime.utcnow().isoformat() + "Z"

                # Re-write file
                new_content = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n\n"
                new_content += "\n\n".join(parts[2:])
                filepath.write_text(new_content, encoding="utf-8")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Memory operations")
    parser.add_argument("command", choices=["save", "describe-repo"])
    parser.add_argument("--config-repo", required=True, help="Path to config repository")
    parser.add_argument("--detail-level", default="normal")
    parser.add_argument("--repo-path", help="Repository path")
    parser.add_argument("--branch", help="Git branch")
    parser.add_argument("--commit", help="Git commit")
    parser.add_argument("--machine", help="Machine identifier")
    parser.add_argument("--os", help="Operating system")
    parser.add_argument("--summary", help="Session summary")
    parser.add_argument("--keywords", help="Comma-separated keywords")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--worktree", help="Worktree path")
    parser.add_argument("--description", help="Repository description")

    args = parser.parse_args()

    ops = ManageMemory(args.config_repo)

    try:
        if args.command == "save":
            result = ops.save_episode(
                detail_level=args.detail_level,
                repo_path=args.repo_path,
                branch=args.branch,
                commit=args.commit,
                machine=args.machine,
                os=args.os,
                summary=args.summary,
                keywords=args.keywords,
                tags=args.tags,
                worktree=args.worktree,
            )
        elif args.command == "describe-repo":
            result = ops.describe_repo(
                repo_path=args.repo_path,
                description=args.description,
                tags=args.tags,
                machine=args.machine,
                os=args.os,
            )

        print(json.dumps(result, indent=2))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 2. `sync_git.py` - Git Synchronization

```python
#!/usr/bin/env python3
"""
Git synchronization operations: pull, commit, push.
"""

import subprocess
from pathlib import Path

class SyncGit:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)

    def pull(self, rebase=True):
        """Pull latest changes from remote."""
        cmd = ["git", "-C", str(self.repo_path), "pull"]
        if rebase:
            cmd.append("--rebase")

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Git pull failed: {result.stderr}")

    def commit_and_push(self, files, message):
        """Commit files and push to remote."""
        # Stage files
        for file in files:
            subprocess.run(
                ["git", "-C", str(self.repo_path), "add", file],
                check=True
            )

        # Commit
        subprocess.run(
            ["git", "-C", str(self.repo_path), "commit", "-m", message],
            check=True,
            capture_output=True
        )

        # Push
        result = subprocess.run(
            ["git", "-C", str(self.repo_path), "push"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise Exception(f"Git push failed: {result.stderr}")
```

### 3. `query_memory.py` - Search and Query

```python
#!/usr/bin/env python3
"""
Search and query memory episodes and repositories.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import yaml

class QueryMemory:
    def __init__(self, config_repo_path):
        self.config_repo = Path(config_repo_path)
        self.memory_dir = self.config_repo / "memory"
        self.episodes_dir = self.memory_dir / "episodes"
        self.repos_dir = self.memory_dir / "repositories"

    def find_repo(self, repo_name):
        """Find all clones of a repository across machines."""
        repo_file = self.repos_dir / f"{repo_name}.md"

        if not repo_file.exists():
            return {"repository": repo_name, "clones": []}

        content = repo_file.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {"repository": repo_name, "clones": []}

        frontmatter = yaml.safe_load(parts[1])
        return {
            "repository": repo_name,
            "clones": frontmatter.get("clones", []),
        }

    def list_recent_repos(self, count=5, filter_type="all"):
        """List recently accessed repositories."""
        repos = []

        for repo_file in self.repos_dir.glob("*.md"):
            content = repo_file.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            frontmatter = yaml.safe_load(parts[1])

            # Find most recent access across all clones
            most_recent = None
            for clone in frontmatter.get("clones", []):
                accessed = clone.get("last_accessed")
                if accessed and (not most_recent or accessed > most_recent):
                    most_recent = accessed

            if most_recent:
                repos.append({
                    "name": frontmatter["repository"]["slug"],
                    "description": frontmatter.get("description", ""),
                    "last_accessed": most_recent,
                    "clones": frontmatter.get("clones", []),
                })

        # Sort by last accessed
        repos.sort(key=lambda x: x["last_accessed"], reverse=True)

        # Apply filter (simplified - could check remote URL for work/personal)
        # For now, return all

        return repos[:count]

    def search_memory(self, query, limit=10):
        """Search memory episodes by keywords."""
        results = []
        keywords = query.lower().split()

        for episode_file in self.episodes_dir.glob("*.md"):
            content = episode_file.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            frontmatter = yaml.safe_load(parts[1])
            body = parts[2]

            # Search in frontmatter and body
            searchable = json.dumps(frontmatter).lower() + " " + body.lower()

            if all(kw in searchable for kw in keywords):
                results.append({
                    "episode_id": frontmatter.get("id"),
                    "timestamp": frontmatter.get("timestamp"),
                    "machine": frontmatter.get("machine"),
                    "os": frontmatter.get("os"),
                    "repository": frontmatter.get("repository", {}).get("name"),
                    "branch": frontmatter.get("repository", {}).get("branch"),
                    "commit": frontmatter.get("repository", {}).get("commit"),
                    "summary": frontmatter.get("summary"),
                })

        # Sort by timestamp (most recent first)
        results.sort(key=lambda x: x["timestamp"], reverse=True)

        return results[:limit]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Query memory")
    parser.add_argument("command", choices=["find-repo", "list-recent-repos", "search-memory"])
    parser.add_argument("--config-repo", required=True)
    parser.add_argument("--repo-name", help="Repository name")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--filter", default="all")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()

    engine = QueryMemory(args.config_repo)

    try:
        if args.command == "find-repo":
            result = engine.find_repo(args.repo_name)
        elif args.command == "list-recent-repos":
            result = engine.list_recent_repos(args.count, args.filter)
        elif args.command == "search-memory":
            result = engine.search_memory(args.query, args.limit)

        print(json.dumps(result, indent=2))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 4. `scan_repos.py` - Repository Discovery

```python
#!/usr/bin/env python3
"""
Scan local repositories and compare with memory system.
"""

import sys
import json
from pathlib import Path
import platform
import yaml

class ScanRepos:
    def __init__(self, config_repo_path):
        self.config_repo = Path(config_repo_path)
        self.repos_dir = self.config_repo / "memory" / "repositories"

    def scan_repos(self, mode="all", machine=None):
        """
        Scan local repositories.

        Args:
            mode: str - all, untracked, missing
            machine: str - machine identifier
        """
        # Determine scan locations
        scan_paths = self._get_scan_paths()

        # Get locally cloned repos
        local_repos = self._scan_local_repos(scan_paths)

        # Get tracked repos from memory
        tracked_repos = self._get_tracked_repos()

        # Compare
        untracked = local_repos - tracked_repos
        missing = tracked_repos - local_repos

        result = {}
        if mode in ["all", "untracked"]:
            result["untracked"] = sorted(list(untracked))
        if mode in ["all", "missing"]:
            result["missing"] = sorted(list(missing))

        return result

    def _get_scan_paths(self):
        """Determine repository scan paths based on OS."""
        paths = []

        if platform.system() == "Windows":
            # Windows: C:\Users\{user}\repos
            user_profile = Path.home()
            paths.append(user_profile / "repos")
        else:
            # Linux/WSL: /home/{user}/repos
            paths.append(Path.home() / "repos")

        return paths

    def _scan_local_repos(self, scan_paths):
        """Scan local directories for git repositories."""
        repos = set()

        for scan_path in scan_paths:
            if not scan_path.exists():
                continue

            for item in scan_path.iterdir():
                if item.is_dir() and (item / ".git").exists():
                    repos.add(item.name)

        return repos

    def _get_tracked_repos(self):
        """Get list of tracked repositories from memory."""
        repos = set()

        for repo_file in self.repos_dir.glob("*.md"):
            repos.add(repo_file.stem)

        return repos


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scan repositories")
    parser.add_argument("command", choices=["scan-repos"])
    parser.add_argument("--config-repo", required=True)
    parser.add_argument("--mode", default="all", choices=["all", "untracked", "missing"])
    parser.add_argument("--machine", help="Machine identifier")

    args = parser.parse_args()

    scanner = ScanRepos(args.config_repo)

    try:
        result = scanner.scan_repos(args.mode, args.machine)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 5. `utils.py` - Common Utilities

```python
#!/usr/bin/env python3
"""
Common utility functions.
"""

import uuid
import platform
import socket
from pathlib import Path

def generate_episode_id():
    """Generate unique episode ID."""
    return f"ep-{uuid.uuid4().hex[:12]}"

def normalize_repo_slug(repo_path, machine=None):
    """
    Generate unique repository slug based on machine + local path.

    See docs/design/07-unique-repository-naming.md for details.
    """
    import hashlib

    repo_name = Path(repo_path).name
    full_path = str(Path(repo_path).resolve()).lower().replace('\\', '/')

    if machine:
        unique_key = f"{machine.lower()}:{full_path}"
    else:
        unique_key = full_path

    path_hash = hashlib.sha256(unique_key.encode('utf-8')).hexdigest()[:8]
    return f"{repo_name}-{path_hash}"

def get_machine_id():
    """Get machine identifier (hostname)."""
    return socket.gethostname().lower()

def get_os_type():
    """Get OS type (windows, linux, darwin)."""
    return platform.system().lower()
```

## Testing

Create unit tests in `tests/` directory:

```python
# tests/test_manage_memory.py
import pytest
from manage_memory import ManageMemory

def test_save_episode(tmp_path):
    # Create temporary config repo
    config_repo = tmp_path / "config"
    config_repo.mkdir()
    (config_repo / "memory" / "episodes").mkdir(parents=True)

    ops = ManageMemory(config_repo)

    result = ops.save_episode(
        detail_level="normal",
        repo_path="/test/repo",
        branch="main",
        commit="abc123",
        machine="test-machine",
        os="linux",
        summary="Test summary",
        keywords="test,memory",
        tags="tag1,tag2"
    )

    assert result["success"] == True
    assert "episode_id" in result
```

Run tests:
```bash
pytest tests/
```
