#!/usr/bin/env python3
"""
Migration script to convert repository metadata files from v1.0 to v2.0 format.

Changes:
- Old naming: {repo_name}.md
- New naming: {repo_name}-{hash}.md (hash based on machine + path)
- Old structure: clones array with multiple locations
- New structure: single location per file

This script will:
1. Read each existing repository metadata file
2. Extract the clones array
3. Create a new file for each clone with the new naming scheme
4. Convert frontmatter from v1.0 to v2.0 format
5. Optionally backup or delete old files
"""

import sys
import json
from pathlib import Path
from datetime import datetime, UTC
import yaml
import shutil

# Import from utils
from utils import normalize_repo_slug


class MigrateRepoFiles:
    """Migrate repository metadata files to new format."""

    def __init__(self, config_repo_path, dry_run=True):
        """
        Initialize migration.

        Args:
            config_repo_path: Path to yoshiwatanabe-configurations repository
            dry_run: If True, only show what would be done without making changes
        """
        self.config_repo = Path(config_repo_path).resolve()
        self.repos_dir = self.config_repo / "domains" / "dev" / "memory" / "repositories"
        self.dry_run = dry_run
        self.backup_dir = self.repos_dir / ".migration_backup"

    def migrate(self):
        """
        Perform migration.

        Returns:
            dict: Migration results
        """
        if not self.repos_dir.exists():
            return {"success": False, "error": "Repositories directory not found"}

        # Create backup directory
        if not self.dry_run:
            self.backup_dir.mkdir(exist_ok=True)

        results = {
            "files_processed": 0,
            "files_created": 0,
            "files_backed_up": 0,
            "errors": [],
            "actions": [],
        }

        # Process each .md file
        for old_file in self.repos_dir.glob("*.md"):
            # Skip hidden files, READMEs, and already-migrated files
            if old_file.name.startswith(".") or old_file.stem.lower() == "readme":
                continue

            # Check if this is already in new format (contains hash)
            # New format: repo-name-12345678.md (ends with 8 hex chars)
            stem_parts = old_file.stem.rsplit("-", 1)
            if len(stem_parts) == 2 and len(stem_parts[1]) == 8 and all(c in "0123456789abcdef" for c in stem_parts[1]):
                results["actions"].append(f"SKIP: {old_file.name} (already in new format)")
                continue

            try:
                self._migrate_file(old_file, results)
                results["files_processed"] += 1
            except Exception as e:
                error_msg = f"Error processing {old_file.name}: {str(e)}"
                results["errors"].append(error_msg)
                print(f"ERROR: {error_msg}")

        return results

    def _migrate_file(self, old_file, results):
        """Migrate a single repository metadata file."""
        print(f"\nProcessing: {old_file.name}")

        # Read existing file
        content = old_file.read_text(encoding="utf-8")
        parts = content.split("---\n", 2)

        if len(parts) < 3:
            raise ValueError("Invalid file format (no frontmatter)")

        frontmatter = yaml.safe_load(parts[1])
        body = parts[2] if len(parts) > 2 else ""

        # Check version
        version = frontmatter.get("version", "1.0")
        if version == "2.0":
            results["actions"].append(f"SKIP: {old_file.name} (already v2.0)")
            return

        # Get repository info
        repo_info = frontmatter.get("repository", {})
        repo_name = repo_info.get("name", old_file.stem)
        remote_url = repo_info.get("remote", "")

        # Get clones array (or create single clone if doesn't exist)
        clones = frontmatter.get("clones", [])

        if not clones:
            # No clones array - this might be an old file or manually created
            # Create a single clone entry as best guess
            print(f"  WARNING: No clones array found, cannot migrate automatically")
            results["actions"].append(f"SKIP: {old_file.name} (no clones array)")
            return

        # Create a new file for each clone
        for i, clone in enumerate(clones):
            machine = clone.get("machine", "unknown")
            os_type = clone.get("os", "unknown")
            path = clone.get("path", "")
            last_accessed = clone.get("last_accessed", datetime.now(UTC).isoformat().replace('+00:00', 'Z'))

            if not path:
                print(f"  WARNING: Clone {i} has no path, skipping")
                continue

            # Generate new filename
            new_slug = normalize_repo_slug(path, machine)
            new_file = self.repos_dir / f"{new_slug}.md"

            print(f"  Clone {i+1}/{len(clones)}: {machine}:{path}")
            print(f"    -> {new_file.name}")

            # Create new frontmatter (v2.0)
            new_frontmatter = {
                "type": "repository-metadata",
                "version": "2.0",
                "repository": {
                    "name": repo_name,
                    "slug": new_slug,
                    "remote": remote_url,
                },
                "location": {
                    "machine": machine,
                    "os": os_type,
                    "path": path,
                    "last_accessed": last_accessed,
                },
            }

            # Copy over description and tags if they exist
            if "description" in frontmatter:
                new_frontmatter["description"] = frontmatter["description"]
            if "tags" in frontmatter:
                new_frontmatter["tags"] = frontmatter["tags"]
            if "archived" in frontmatter:
                new_frontmatter["archived"] = frontmatter["archived"]
                if "archived_date" in frontmatter:
                    new_frontmatter["archived_date"] = frontmatter["archived_date"]
                if "archived_reason" in frontmatter:
                    new_frontmatter["archived_reason"] = frontmatter["archived_reason"]

            # Build new content
            new_content = f"---\n{yaml.dump(new_frontmatter, default_flow_style=False, sort_keys=False)}---\n\n"
            new_content += body

            # Write new file (if not dry run)
            if not self.dry_run:
                new_file.write_text(new_content, encoding="utf-8")
                results["files_created"] += 1
            else:
                print(f"    [DRY RUN] Would create: {new_file.name}")

            results["actions"].append(f"CREATE: {new_file.name} from {old_file.name} clone {i+1}")

        # Backup old file
        if not self.dry_run:
            backup_file = self.backup_dir / old_file.name
            shutil.copy2(old_file, backup_file)
            results["files_backed_up"] += 1
            print(f"  Backed up to: {backup_file.relative_to(self.config_repo)}")

            # Delete old file
            old_file.unlink()
            print(f"  Deleted: {old_file.name}")
            results["actions"].append(f"DELETE: {old_file.name} (backed up)")
        else:
            print(f"  [DRY RUN] Would backup and delete: {old_file.name}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate repository metadata files from v1.0 to v2.0 format"
    )
    parser.add_argument(
        "--config-repo",
        required=True,
        help="Path to yoshiwatanabe-configurations repository",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be done without making changes (default: True)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the migration (turns off dry-run)",
    )

    args = parser.parse_args()

    # If --execute is specified, turn off dry-run
    dry_run = not args.execute

    print("=" * 70)
    print("Repository Metadata Migration: v1.0 -> v2.0")
    print("=" * 70)
    print(f"Config repo: {args.config_repo}")
    print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'EXECUTE (will modify files)'}")
    print("=" * 70)

    if not dry_run:
        print("\nWARNING: This will modify your repository metadata files!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            print("Migration cancelled.")
            sys.exit(0)

    migrator = MigrateRepoFiles(args.config_repo, dry_run=dry_run)

    try:
        results = migrator.migrate()

        print("\n" + "=" * 70)
        print("Migration Results:")
        print("=" * 70)
        print(f"Files processed: {results['files_processed']}")
        print(f"Files created: {results['files_created']}")
        print(f"Files backed up: {results['files_backed_up']}")
        print(f"Errors: {len(results['errors'])}")

        if results['errors']:
            print("\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")

        if dry_run:
            print("\n" + "=" * 70)
            print("This was a DRY RUN. No files were modified.")
            print("To perform the migration, run with --execute flag:")
            print(f"  python migrate_repo_files.py --config-repo \"{args.config_repo}\" --execute")
            print("=" * 70)

        print(json.dumps(results, indent=2))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
