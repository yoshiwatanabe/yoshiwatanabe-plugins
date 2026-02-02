#!/usr/bin/env python3
"""
Common utility functions for memory management.
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

    Ensures each working directory on each machine gets its own metadata file,
    even if:
    - Multiple directories point to the same remote repository
    - Same directory path exists on different machines
    - Different directories have the same name

    Args:
        repo_path: Local path to repository
        machine: Machine identifier (hostname)

    Returns:
        Unique slug in format: {repo_name}-{hash}

    Examples:
        Machine A, C:\\repos\\xyz -> xyz-a1b2c3d4
        Machine B, C:\\repos\\xyz -> xyz-e5f6g7h8
        Machine A, C:\\repos\\xyz-test -> xyz-test-f9g0h1i2
    """
    import hashlib

    repo_name = Path(repo_path).name

    # Normalize path for consistent hashing across different path representations
    # Use lowercase and forward slashes for consistency
    full_path = str(Path(repo_path).resolve()).lower().replace('\\', '/')

    # Generate unique key combining machine and path
    if machine:
        unique_key = f"{machine.lower()}:{full_path}"
    else:
        # Fallback if machine not provided (for backwards compatibility)
        # In practice, machine should always be provided
        unique_key = full_path

    # Generate short hash (8 chars = 4 billion+ possibilities)
    path_hash = hashlib.sha256(unique_key.encode('utf-8')).hexdigest()[:8]

    return f"{repo_name}-{path_hash}"


def get_machine_id():
    """Get machine identifier (hostname)."""
    return socket.gethostname().lower()


def get_os_type():
    """Get OS type (windows, linux, darwin)."""
    system = platform.system().lower()
    if system == "linux":
        # Check if running in WSL
        try:
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    return "wsl"
        except Exception:
            pass
    return system
