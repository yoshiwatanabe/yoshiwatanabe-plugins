#!/usr/bin/env python3
"""
Git synchronization operations: pull, commit, push.
"""

import subprocess
from pathlib import Path


class SyncGit:
    """Handle git synchronization for the configuration repository."""

    def __init__(self, repo_path):
        """
        Initialize git sync.

        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = Path(repo_path)
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {repo_path}")

    def pull(self, rebase=True):
        """
        Pull latest changes from remote.

        Args:
            rebase: Use rebase instead of merge (default: True)

        Raises:
            Exception: If git pull fails
        """
        cmd = ["git", "-C", str(self.repo_path), "pull"]
        if rebase:
            cmd.append("--rebase")

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Git pull failed: {result.stderr}")

        return result.stdout.strip()

    def commit_and_push(self, files, message):
        """
        Commit files and push to remote.

        Args:
            files: List of file paths relative to repo root
            message: Commit message

        Raises:
            Exception: If git operations fail
        """
        # Stage files
        for file in files:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "add", file],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise Exception(f"Git add failed for {file}: {result.stderr}")

        # Commit
        result = subprocess.run(
            ["git", "-C", str(self.repo_path), "commit", "-m", message],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            # Check if it's a "nothing to commit" error
            if "nothing to commit" not in result.stdout.lower():
                raise Exception(f"Git commit failed: {result.stderr}")

        # Push
        result = subprocess.run(
            ["git", "-C", str(self.repo_path), "push"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise Exception(f"Git push failed: {result.stderr}")

        return result.stdout.strip()

    def status(self):
        """Get git status."""
        result = subprocess.run(
            ["git", "-C", str(self.repo_path), "status", "--short"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
