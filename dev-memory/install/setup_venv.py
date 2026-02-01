#!/usr/bin/env python3
"""Set up Python virtual environment and install dependencies."""

import sys
import subprocess
from pathlib import Path


def setup_venv():
    """Set up Python virtual environment and install dependencies."""
    plugin_dir = Path(__file__).parent.parent
    venv_dir = plugin_dir / "venv"
    requirements = plugin_dir / "requirements.txt"

    print("Setting up Python virtual environment...")

    # Create venv
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

    # Determine pip path
    if sys.platform == "win32":
        pip_path = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_path = venv_dir / "bin" / "pip"

    # Install dependencies
    print("Installing dependencies...")
    subprocess.run([str(pip_path), "install", "-r", str(requirements)], check=True)

    print("✅ Virtual environment setup complete!")


if __name__ == "__main__":
    setup_venv()
