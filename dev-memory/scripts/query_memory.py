#!/usr/bin/env python3
"""
Search and query memory episodes and repositories.
"""

import sys
import json
from pathlib import Path
import yaml


class QueryMemory:
    """Query memory episodes and repository metadata."""

    def __init__(self, config_repo_path):
        """
        Initialize query engine.

        Args:
            config_repo_path: Path to yoshiwatanabe-configurations repository
        """
        self.config_repo = Path(config_repo_path).resolve()
        self.dev_domain = self.config_repo / "domains" / "dev"
        self.memory_dir = self.dev_domain / "memory"
        self.episodes_dir = self.memory_dir / "episodes"
        self.repos_dir = self.memory_dir / "repositories"

    def find_repo(self, repo_name):
        """
        Find all clones of a repository across machines.

        Args:
            repo_name: Repository name or slug

        Returns:
            dict: Repository name and list of clones
        """
        repo_file = self.repos_dir / f"{repo_name}.md"

        if not repo_file.exists():
            return {"repository": repo_name, "clones": [], "found": False}

        content = repo_file.read_text(encoding="utf-8")
        parts = content.split("---\n", 2)
        if len(parts) < 3:
            return {"repository": repo_name, "clones": [], "found": False}

        frontmatter = yaml.safe_load(parts[1])
        return {
            "repository": repo_name,
            "description": frontmatter.get("description", ""),
            "clones": frontmatter.get("clones", []),
            "tags": frontmatter.get("tags", []),
            "archived": frontmatter.get("archived", False),
            "archived_date": frontmatter.get("archived_date"),
            "archived_reason": frontmatter.get("archived_reason"),
            "found": True,
        }

    def list_recent_repos(self, count=5, filter_type="all", include_archived=False):
        """
        List recently accessed repositories.

        Args:
            count: Number of repositories to return
            filter_type: Filter by machine type (work, personal, all)
            include_archived: If True, include archived repositories (default: False)

        Returns:
            list: Recently accessed repositories
        """
        repos = []

        for repo_file in self.repos_dir.glob("*.md"):
            content = repo_file.read_text(encoding="utf-8")
            parts = content.split("---\n", 2)
            if len(parts) < 3:
                continue

            frontmatter = yaml.safe_load(parts[1])

            # Skip archived repositories unless explicitly requested
            if not include_archived and frontmatter.get("archived", False):
                continue

            # Find most recent access across all clones
            most_recent = None
            most_recent_clone = None
            for clone in frontmatter.get("clones", []):
                accessed = clone.get("last_accessed")
                if accessed and (not most_recent or accessed > most_recent):
                    most_recent = accessed
                    most_recent_clone = clone

            if most_recent:
                repos.append({
                    "name": frontmatter["repository"]["slug"],
                    "description": frontmatter.get("description", ""),
                    "last_accessed": most_recent,
                    "last_machine": most_recent_clone.get("machine") if most_recent_clone else None,
                    "last_os": most_recent_clone.get("os") if most_recent_clone else None,
                    "clones": frontmatter.get("clones", []),
                    "tags": frontmatter.get("tags", []),
                    "archived": frontmatter.get("archived", False),
                })

        # Sort by last accessed (most recent first)
        repos.sort(key=lambda x: x["last_accessed"], reverse=True)

        # Apply filter (simplified - could check remote URL for work/personal)
        # For now, return all
        if filter_type != "all":
            # TODO: Implement filtering logic based on remote URL or tags
            pass

        return repos[:count]

    def search_memory(self, query, limit=10):
        """
        Search memory episodes by keywords.

        Args:
            query: Search query (keywords)
            limit: Maximum number of results

        Returns:
            list: Matching memory episodes
        """
        results = []
        keywords = query.lower().split()

        for episode_file in self.episodes_dir.glob("*.md"):
            content = episode_file.read_text(encoding="utf-8")
            parts = content.split("---\n", 2)
            if len(parts) < 3:
                continue

            frontmatter = yaml.safe_load(parts[1])
            body = parts[2] if len(parts) > 2 else ""

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
                    "keywords": frontmatter.get("keywords", []),
                    "tags": frontmatter.get("context", {}).get("tags", []),
                })

        # Sort by timestamp (most recent first)
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

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
    parser.add_argument("--include-archived", action="store_true", help="Include archived repositories")

    args = parser.parse_args()

    engine = QueryMemory(args.config_repo)

    try:
        if args.command == "find-repo":
            result = engine.find_repo(args.repo_name)
        elif args.command == "list-recent-repos":
            result = engine.list_recent_repos(args.count, args.filter, args.include_archived)
        elif args.command == "search-memory":
            result = engine.search_memory(args.query, args.limit)

        print(json.dumps(result, indent=2))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
