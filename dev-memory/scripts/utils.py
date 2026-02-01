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


def normalize_repo_slug(repo_path):
    """Extract repository slug from path."""
    return Path(repo_path).name


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
