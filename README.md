# yoshiwatanabe-plugins

Personal Claude Code plugins for domain-specific memory and configuration management.

## Plugins

### `dev-memory/` - Development Domain Memory

Track coding sessions, repositories, and development work across multiple machines.

**Features:**
- Save coding session progress
- Repository metadata management
- Cross-machine repository discovery
- Memory search by keywords
- Local repository scanning
- Archive/unarchive obsolete repositories

**Status:** ✅ Production Ready

[View Documentation →](dev-memory/README.md)

### Future Plugins

- `health/` - Health and medical tracking
- `vehicles/` - Vehicle maintenance and specs
- `finance/` - Financial planning and allocations

## Architecture

Each plugin is domain-focused and independent:
- Has its own skills, agents, and scripts
- Manages domain-specific memory and configuration
- Stores data in separate domain directories
- Can be installed and used independently

## Installation

**[📖 View Complete Installation Guide →](INSTALL.md)**

### Quick Start

```
/plugin marketplace add yoshiwatanabe/yoshiwatanabe-plugins
/plugin install yoshiwatanabe-dev@yoshiwatanabe-plugins
claude config set yoshiwatanabe-dev.configRepoPath "/path/to/your-config-repo"
```

## Configuration Repository

Plugins require a configuration repository with domain structure:

```
your-config-repo/
├── domains/
│   ├── dev/           # Development domain
│   ├── health/        # Health domain (future)
│   ├── vehicles/      # Vehicles domain (future)
│   └── finance/       # Finance domain (future)
└── machines/          # Cross-domain machine configs
```

## Contributing

Issues and pull requests welcome!

## License

MIT
