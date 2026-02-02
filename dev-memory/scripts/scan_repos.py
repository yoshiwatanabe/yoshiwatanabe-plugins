#!/usr/bin/env python3
"""
Scan local repositories and compare with memory system.
"""

import sys
import json
from pathlib import Path
import platform
import yaml
from utils import normalize_repo_slug, get_machine_id, get_os_type


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
            machine: Machine identifier (optional, will be auto-detected)

        Returns:
            dict: Scan results with untracked and/or missing repos
        """
        # Auto-detect machine if not provided
        if not machine:
            machine = get_machine_id()

        # Determine scan locations
        scan_paths = self._get_scan_paths()

        # Get locally cloned repos with their hashed slugs
        local_repos = self._scan_local_repos(scan_paths, machine)

        # Get tracked repos from memory
        tracked_repos = self._get_tracked_repos()

        # Compare slugs
        local_slugs = set(repo['slug'] for repo in local_repos)
        tracked_slugs = set(tracked_repos.keys())

        untracked_slugs = local_slugs - tracked_slugs
        missing_slugs = tracked_slugs - local_slugs

        result = {}
        if mode in ["all", "untracked"]:
            result["untracked"] = sorted([
                {"name": repo['name'], "path": repo['path'], "slug": repo['slug']}
                for repo in local_repos if repo['slug'] in untracked_slugs
            ], key=lambda x: x['name'])
        if mode in ["all", "missing"]:
            result["missing"] = sorted([
                {"slug": slug, "info": tracked_repos[slug]}
                for slug in missing_slugs
            ], key=lambda x: x['slug'])

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

    def _scan_local_repos(self, scan_paths, machine):
        """Scan local directories for git repositories."""
        repos = []

        for scan_path in scan_paths:
            if not scan_path.exists():
                continue

            for item in scan_path.iterdir():
                if item.is_dir() and (item / ".git").exists():
                    # Generate the same slug that would be used in memory system
                    slug = normalize_repo_slug(str(item), machine)
                    repos.append({
                        'name': item.name,
                        'path': str(item),
                        'slug': slug
                    })

        return repos

    def _get_tracked_repos(self):
        """Get list of tracked repositories from memory."""
        repos = {}

        if not self.repos_dir.exists():
            return repos

        for repo_file in self.repos_dir.glob("*.md"):
            # Exclude hidden files and READMEs
            if repo_file.name.startswith(".") or repo_file.stem.lower() == "readme":
                continue

            # Read metadata to get location info
            try:
                content = repo_file.read_text(encoding="utf-8")
                parts = content.split("---\n", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    location = frontmatter.get("location", {})
                    repos[repo_file.stem] = {
                        "path": location.get("path", "unknown"),
                        "machine": location.get("machine", "unknown"),
                        "os": location.get("os", "unknown"),
                    }
            except Exception:
                # If we can't parse the file, just use the slug
                repos[repo_file.stem] = {"path": "unknown", "machine": "unknown", "os": "unknown"}

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
