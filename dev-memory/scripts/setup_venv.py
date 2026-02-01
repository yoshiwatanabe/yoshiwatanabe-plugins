#!/usr/bin/env python3
"""
Setup virtual environment and install dependencies.
Run automatically by Claude Code after plugin installation.
"""
import sys
import subprocess
from pathlib import Path


def setup_venv():
    """Create venv and install dependencies."""
    # Plugin root is the parent of scripts/
    plugin_root = Path(__file__).parent.parent
    venv_dir = plugin_root / "venv"
    requirements = plugin_root / "requirements.txt"

    print(f"Setting up Python virtual environment in {plugin_root}")

    # Create venv
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

    # Determine pip path
    if sys.platform == "win32":
        pip_path = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_path = venv_dir / "bin" / "pip"

    # Install dependencies
    print("Installing dependencies from requirements.txt...")
    subprocess.run([str(pip_path), "install", "-r", str(requirements)], check=True)

    print("✅ Virtual environment setup complete!")


if __name__ == "__main__":
    try:
        setup_venv()
    except Exception as e:
        print(f"❌ Error setting up venv: {e}", file=sys.stderr)
        sys.exit(1)
