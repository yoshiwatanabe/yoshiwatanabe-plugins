# yoshiwatanabe-dev Plugin Documentation

This directory contains comprehensive documentation for the yoshiwatanabe-dev plugin (development domain memory management).

## Quick Links

- [Installation Guide](../INSTALL.md) - Setup instructions for all platforms
- [User Guide](../dev-memory/README.md) - How to use the plugin
- [Versioning Policy](../VERSIONING.md) - Version numbering strategy

## Architecture & Design

The `design/` directory contains the complete design documentation created during plugin development:

1. **[00-README.md](design/00-README.md)** - Design overview and goals
2. **[01-architecture-overview.md](design/01-architecture-overview.md)** - System architecture and components
3. **[02-data-model.md](design/02-data-model.md)** - Memory episode and repository data structures
4. **[03-plugin-structure.md](design/03-plugin-structure.md)** - Plugin directory layout and organization
5. **[04-skills-definition.md](design/04-skills-definition.md)** - All skills and their implementations
6. **[05-subagent-definition.md](design/05-subagent-definition.md)** - Memory manager subagent specification
7. **[06-python-implementation.md](design/06-python-implementation.md)** - Python scripts for data management
8. **[07-implementation-roadmap.md](design/07-implementation-roadmap.md)** - Development phases and milestones

## Key Concepts

### Data vs Logic Separation

- **Plugin Repository** (yoshiwatanabe-plugins): Contains LOGIC
  - Skills definitions
  - Agent specifications
  - Python scripts for data operations

- **Configuration Repository** (yoshiwatanabe-configurations): Contains DATA
  - Memory episodes (markdown files with YAML frontmatter)
  - Repository metadata
  - Machine configurations

### Semantic Search Architecture

Version 2.0 introduced semantic search using Claude's language understanding:
- No keyword matching or grep
- Agent reads episode YAML frontmatter
- Uses semantic understanding to find relevant episodes
- Explains why each episode matches the query

### Cross-Machine Tracking

The plugin tracks development work across multiple machines:
- Each machine has unique hostname
- Episodes record machine, OS, repository, and commit
- Repository metadata tracks all clones across machines
- Skills show machine location to help user navigate

## Development Guidelines

### Version Numbering

Follow semantic versioning (MAJOR.MINOR.PATCH):
- **Major**: Breaking changes to skill APIs or data format
- **Minor**: New features (new skills, major enhancements)
- **Patch**: Bug fixes, cross-platform improvements, documentation

### Cross-Platform Support

Always test on:
- Windows (native paths: `C:\Users\...`)
- WSL (mounted paths: `/mnt/c/users/...`)
- Linux (native Unix paths: `/home/...`)

Use environment variable `YW_CONFIG_REPO_PATH` for flexible configuration.

### Skill Design Principles

1. **User-invocable skills** - Use `user-invocable: true` for skills users call directly
2. **Agent-based execution** - Heavy operations use memory-manager subagent
3. **Clear error messages** - Include examples and troubleshooting steps
4. **Machine-agnostic examples** - Use "username" placeholder, not specific usernames

## Contributing

When adding new features:
1. Update relevant design docs if architecture changes
2. Bump version appropriately
3. Test cross-platform compatibility
4. Update skill documentation with examples
5. Consider token usage (use subagents for large operations)

## Support

- Issues: https://github.com/yoshiwatanabe/yoshiwatanabe-plugins/issues
- Repository: https://github.com/yoshiwatanabe/yoshiwatanabe-plugins
