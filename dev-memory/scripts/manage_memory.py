#!/usr/bin/env python3
"""
Core memory operations: save episodes, manage repository metadata.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, UTC
import yaml

from sync_git import SyncGit
from utils import generate_episode_id, normalize_repo_slug


class ManageMemory:
    """Manage memory episodes and repository metadata."""

    def __init__(self, config_repo_path):
        """
        Initialize memory manager.

        Args:
            config_repo_path: Path to yoshiwatanabe-configurations repository
        """
        self.config_repo = Path(config_repo_path).resolve()
        self.dev_domain = self.config_repo / "domains" / "dev"
        self.memory_dir = self.dev_domain / "memory"
        self.episodes_dir = self.memory_dir / "episodes"
        self.repos_dir = self.memory_dir / "repositories"
        self.machines_dir = self.memory_dir / "machines"

        # Ensure directories exist
        self.episodes_dir.mkdir(parents=True, exist_ok=True)
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        self.machines_dir.mkdir(parents=True, exist_ok=True)

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
            os: str - operating system (windows, linux, wsl)
            summary: str - session summary
            keywords: str - comma-separated keywords (optional)
            tags: str - comma-separated tags (optional)
            worktree: str - worktree path (optional)

        Returns:
            dict: Result with episode_id, filepath, synced status
        """
        # Note: No automatic pull - users can pull manually when needed
        # If push fails due to being behind, git will show clear error

        # Generate episode metadata
        episode_id = generate_episode_id()
        timestamp = datetime.now(UTC).isoformat().replace('+00:00', 'Z')
        repo_slug = normalize_repo_slug(kwargs["repo_path"])

        # Build filename
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")
        filename = f"{date_str}_{kwargs['machine']}_{kwargs['os']}_{repo_slug}_{episode_id}.md"
        filepath = self.episodes_dir / filename

        # Get remote URL
        remote_url = self._get_remote_url(kwargs["repo_path"])

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
                "remote": remote_url,
                "branch": kwargs["branch"],
                "commit": kwargs["commit"],
            },
            "context": {
                "detail_level": kwargs.get("detail_level", "normal"),
                "tags": kwargs.get("tags", "").split(",") if kwargs.get("tags") else [],
            },
            "summary": kwargs["summary"],
            "keywords": kwargs.get("keywords", "").split(",") if kwargs.get("keywords") else [],
        }

        if kwargs.get("worktree"):
            frontmatter["repository"]["worktree"] = kwargs["worktree"]

        # Write episode file
        content = f"---\n{yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)}---\n\n"
        content += f"# Memory Episode: {kwargs['summary']}\n\n"
        content += "## Context\n\n"
        content += f"- **Machine:** {kwargs['machine']}\n"
        content += f"- **OS:** {kwargs['os']}\n"
        content += f"- **Repository:** {repo_slug}\n"
        content += f"- **Branch:** {kwargs['branch']}\n"
        content += f"- **Commit:** {kwargs['commit']}\n\n"
        content += "## Summary\n\n"
        content += f"{kwargs['summary']}\n"

        filepath.write_text(content, encoding="utf-8")
        print(f"Created episode: {filepath.relative_to(self.config_repo)}")

        # Update repository metadata
        self._update_repo_metadata(repo_slug, kwargs, remote_url)

        # Commit and push
        print("Committing and pushing changes...")
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
            tags: str - comma-separated tags (optional)
            machine: str - current machine
            os: str - current OS

        Returns:
            dict: Result with repo_slug and filepath
        """
        # Note: No automatic pull - users can pull manually when needed
        # If push fails due to being behind, git will show clear error

        repo_slug = normalize_repo_slug(kwargs["repo_path"])
        filepath = self.repos_dir / f"{repo_slug}.md"
        remote_url = self._get_remote_url(kwargs["repo_path"])

        # Load existing metadata if present
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
            else:
                frontmatter = self._create_repo_frontmatter(repo_slug, remote_url)
        else:
            frontmatter = self._create_repo_frontmatter(repo_slug, remote_url)

        # Update metadata
        frontmatter["description"] = kwargs["description"]
        frontmatter["tags"] = kwargs.get("tags", "").split(",") if kwargs.get("tags") else []

        # Update or add clone info
        clone_info = {
            "machine": kwargs["machine"],
            "os": kwargs["os"],
            "path": kwargs["repo_path"],
            "last_accessed": datetime.now(UTC).isoformat().replace('+00:00', 'Z'),
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
        content = f"---\n{yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)}---\n\n"
        content += f"# Repository: {repo_slug}\n\n"
        content += f"## Description\n\n{kwargs['description']}\n\n"

        filepath.write_text(content, encoding="utf-8")
        print(f"Updated repository: {filepath.relative_to(self.config_repo)}")

        # Commit and push
        print("Committing and pushing changes...")
        self.git_sync.commit_and_push(
            files=[str(filepath.relative_to(self.config_repo))],
            message=f"Update repository metadata: {repo_slug}"
        )

        return {
            "success": True,
            "repo_slug": repo_slug,
            "filepath": str(filepath.relative_to(self.config_repo)),
        }

    def archive_repo(self, **kwargs):
        """
        Archive (hide) a repository.

        Args:
            repo_name: str - repository name/slug
            reason: str - optional reason for archiving

        Returns:
            dict: Result with repo_slug and filepath
        """
        # Note: No automatic pull - users can pull manually when needed
        # If push fails due to being behind, git will show clear error

        repo_slug = kwargs["repo_name"]
        filepath = self.repos_dir / f"{repo_slug}.md"

        if not filepath.exists():
            return {
                "success": False,
                "error": f"Repository '{repo_slug}' not found in memory system"
            }

        # Load existing metadata
        content = filepath.read_text(encoding="utf-8")
        parts = content.split("---\n", 2)
        if len(parts) < 3:
            return {"success": False, "error": "Invalid repository metadata format"}

        frontmatter = yaml.safe_load(parts[1])

        # Mark as archived
        frontmatter["archived"] = True
        frontmatter["archived_date"] = datetime.now(UTC).isoformat().replace('+00:00', 'Z')
        if kwargs.get("reason"):
            frontmatter["archived_reason"] = kwargs["reason"]

        # Write file
        new_content = f"---\n{yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)}---\n\n"
        if len(parts) > 2:
            new_content += parts[2]

        filepath.write_text(new_content, encoding="utf-8")
        print(f"Archived repository: {filepath.relative_to(self.config_repo)}")

        # Commit and push
        print("Committing and pushing changes...")
        self.git_sync.commit_and_push(
            files=[str(filepath.relative_to(self.config_repo))],
            message=f"Archive repository: {repo_slug}"
        )

        return {
            "success": True,
            "repo_slug": repo_slug,
            "archived": True,
            "filepath": str(filepath.relative_to(self.config_repo)),
        }

    def unarchive_repo(self, **kwargs):
        """
        Unarchive (restore) a repository.

        Args:
            repo_name: str - repository name/slug

        Returns:
            dict: Result with repo_slug and filepath
        """
        # Note: No automatic pull - users can pull manually when needed
        # If push fails due to being behind, git will show clear error

        repo_slug = kwargs["repo_name"]
        filepath = self.repos_dir / f"{repo_slug}.md"

        if not filepath.exists():
            return {
                "success": False,
                "error": f"Repository '{repo_slug}' not found in memory system"
            }

        # Load existing metadata
        content = filepath.read_text(encoding="utf-8")
        parts = content.split("---\n", 2)
        if len(parts) < 3:
            return {"success": False, "error": "Invalid repository metadata format"}

        frontmatter = yaml.safe_load(parts[1])

        # Unarchive
        frontmatter["archived"] = False
        if "archived_date" in frontmatter:
            del frontmatter["archived_date"]
        if "archived_reason" in frontmatter:
            del frontmatter["archived_reason"]

        # Write file
        new_content = f"---\n{yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)}---\n\n"
        if len(parts) > 2:
            new_content += parts[2]

        filepath.write_text(new_content, encoding="utf-8")
        print(f"Unarchived repository: {filepath.relative_to(self.config_repo)}")

        # Commit and push
        print("Committing and pushing changes...")
        self.git_sync.commit_and_push(
            files=[str(filepath.relative_to(self.config_repo))],
            message=f"Unarchive repository: {repo_slug}"
        )

        return {
            "success": True,
            "repo_slug": repo_slug,
            "archived": False,
            "filepath": str(filepath.relative_to(self.config_repo)),
        }

    def _get_remote_url(self, repo_path):
        """Get git remote URL for a repository."""
        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _create_repo_frontmatter(self, repo_slug, remote_url):
        """Create initial repository frontmatter."""
        return {
            "type": "repository-metadata",
            "version": "1.0",
            "repository": {
                "name": repo_slug,
                "slug": repo_slug,
                "remote": remote_url,
            },
            "clones": [],
        }

    def _update_repo_metadata(self, repo_slug, context, remote_url):
        """Update repository metadata with latest access time."""
        filepath = self.repos_dir / f"{repo_slug}.md"

        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])

                # Update last_accessed for matching clone
                for clone in frontmatter.get("clones", []):
                    if clone["machine"] == context["machine"] and clone["os"] == context["os"]:
                        clone["last_accessed"] = datetime.now(UTC).isoformat().replace('+00:00', 'Z')
                        break
                else:
                    # Clone not found, add it
                    frontmatter.setdefault("clones", []).append({
                        "machine": context["machine"],
                        "os": context["os"],
                        "path": context["repo_path"],
                        "last_accessed": datetime.now(UTC).isoformat().replace('+00:00', 'Z'),
                    })

                # Re-write file
                new_content = f"---\n{yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)}---\n\n"
                if len(parts) > 2:
                    new_content += parts[2]
                filepath.write_text(new_content, encoding="utf-8")

                # Add to git
                self.git_sync.commit_and_push(
                    files=[str(filepath.relative_to(self.config_repo))],
                    message=f"Update repository access time: {repo_slug}"
                )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Manage memory operations")
    parser.add_argument("command", choices=["save", "describe-repo", "archive-repo", "unarchive-repo"])
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
    parser.add_argument("--repo-name", help="Repository name/slug")
    parser.add_argument("--reason", help="Reason for archiving (optional)")

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
        elif args.command == "archive-repo":
            result = ops.archive_repo(
                repo_name=args.repo_name,
                reason=args.reason,
            )
        elif args.command == "unarchive-repo":
            result = ops.unarchive_repo(
                repo_name=args.repo_name,
            )

        print(json.dumps(result, indent=2))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
