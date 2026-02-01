#!/usr/bin/env python3
"""
Scan local repositories and compare with memory system.
"""

import sys
import json
from pathlib import Path
import platform


class ScanRepos:
    """Scan local repositories and identify untracked/missing repos."""

    def __init__(self, config_repo_path):
        """
        Initialize repository scanner.

        Args:
            config_repo_path: Path to yoshiwatanabe-configurations repository
        """
        self.config_repo = Path(config_repo_path).resolve()
        self.dev_domain = self.config_repo / "domains" / "dev"
        self.repos_dir = self.dev_domain / "memory" / "repositories"

    def scan_repos(self, mode="all", machine=None):
        """
        Scan local repositories.

        Args:
            mode: Scan mode (all, untracked, missing)
            machine: Machine identifier (optional)

        Returns:
            dict: Scan results with untracked and/or missing repos
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

        result["scan_paths"] = [str(p) for p in scan_paths]
        result["total_local"] = len(local_repos)
        result["total_tracked"] = len(tracked_repos)

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

        return [p for p in paths if p.exists()]

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

        if not self.repos_dir.exists():
            return repos

        for repo_file in self.repos_dir.glob("*.md"):
            # Exclude hidden files and READMEs
            if not repo_file.name.startswith(".") and repo_file.stem.lower() != "readme":
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
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
