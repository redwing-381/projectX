# ProjectX CLI

Command-line interface for ProjectX - a smart notification bridge that monitors your email and sends SMS alerts for urgent messages.

## Installation

```bash
pip install projectx-cli
```

## Usage

### Check Server Status

```bash
projectx status
```

### Trigger Email Check

```bash
projectx check
```

This will:
1. Fetch unread emails from your Gmail
2. Classify each email using AI (URGENT or NOT_URGENT)
3. Send SMS alerts for urgent emails

### Test Classification

```bash
projectx test
```

Tests the AI classification and SMS flow with a sample urgent email.

### Configuration

```bash
# View current config
projectx config show

# Set custom server URL
projectx config set-url https://your-server.up.railway.app
```

### JSON Output

All commands support `--json` flag for machine-readable output:

```bash
projectx status --json
projectx check --json
```

## Configuration

Config is stored at `~/.projectx/config.json`

Default server: `https://projectx-production-0eeb.up.railway.app`

## Requirements

- Python 3.9+
- A running ProjectX server (deployed on Railway or elsewhere)

## License

MIT
