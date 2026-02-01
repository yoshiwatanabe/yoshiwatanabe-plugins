# Versioning Guide

This project follows [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

## Version Format

**X.Y.Z** where:
- **X (MAJOR)**: Breaking changes - users must update their configuration or usage
- **Y (MINOR)**: New features - backward compatible, users can update safely
- **Z (PATCH)**: Bug fixes - always safe to update

## When to Bump

### MAJOR (X.0.0) - Breaking Changes
- Changed skill names or parameters
- Removed features
- Changed data model (breaks existing memory files)
- Changed configuration format
- Changed required environment variables

### MINOR (0.Y.0) - New Features
- New skills added
- New parameters added to existing skills (optional)
- Enhanced functionality
- Performance improvements
- New configuration options (optional)

### PATCH (0.0.Z) - Bug Fixes
- Fixed broken functionality
- Documentation updates
- Error message improvements
- Security patches

## Release Checklist

Before pushing to main:

1. **Update version** in `dev-memory/.claude-plugin/plugin.json`
2. **Commit with version** in message: "Bump version to X.Y.Z"
3. **Document changes** in commit message
4. **Tag release** (optional): `git tag v1.1.0 && git push --tags`

## Version History

### 1.1.0 (Current)
- ✨ NEW: Archive/unarchive repositories
- 🔧 Use CLAUDE_PLUGIN_ROOT for deterministic paths
- ⚡ Remove automatic git pull
- 🛡️ Graceful venv fallback
- 📝 WSL path documentation

### 1.0.0 (Initial Release)
- Initial marketplace release
- 8 core skills
- Cross-machine memory sync
- Repository tracking
