# ProjectX CLI

Command-line interface for ProjectX - a smart notification bridge that monitors your email and mobile notifications, uses AI to detect urgency, and sends SMS alerts to your keypad phone.

## Installation

```bash
pip install projectx-cli
```

## Quick Start

```bash
# Login with your API key
projectx login

# Check server status
projectx status

# Test AI classification (sends SMS if urgent)
projectx test
```

## Commands

### Authentication

```bash
projectx login          # Authenticate with API key
projectx logout         # Remove saved credentials
```

### Main Commands

```bash
projectx status         # Check server health and pipeline status
projectx check          # Trigger email check and display results
projectx test           # Test classification with sample urgent email
projectx help           # Show all available commands
```

### Monitor Commands

Control scheduled email monitoring:

```bash
projectx monitor status              # Show monitoring status
projectx monitor start               # Enable email monitoring
projectx monitor stop                # Disable email monitoring
projectx monitor set-interval 5      # Set check interval (1-1440 minutes)
```

### Config Commands

```bash
projectx config show                 # Display current configuration
projectx config set-url <url>        # Set custom server URL
```

### JSON Output

All commands support `--json` flag for machine-readable output:

```bash
projectx status --json
projectx check --json
projectx monitor status --json
```

## Configuration

Config is stored at `~/.projectx/config.json`

Default server: `https://projectx-solai.up.railway.app`

## Requirements

- Python 3.9+
- A running ProjectX server

## Links

- **Web Dashboard**: https://projectx-solai.up.railway.app
- **GitHub**: https://github.com/redwing-381/projectX

## License

MIT
