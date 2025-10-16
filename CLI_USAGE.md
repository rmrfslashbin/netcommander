# NetCommander CLI Usage Guide

The NetCommander CLI provides a command-line interface to control Synaccess netCommander PDUs.

## Installation

```bash
# Install from local directory with CLI dependencies
uv pip install -e ".[cli]"
```

## Configuration

The CLI can be configured using environment variables or command-line options.

### Environment Variables (.env file)

```bash
NETCOMMANDER_HOST=192.168.1.100
NETCOMMANDER_USER=admin
NETCOMMANDER_PASSWORD=your_password
```

### Command-Line Options

```bash
--host TEXT          Device IP address
-u, --username TEXT  Username (default: admin)
-p, --password TEXT  Password
```

## Commands

### Show Status

Display the current state of all outlets:

```bash
# Table format (default)
python -m netcommander_cli.cli status

# JSON format
python -m netcommander_cli.cli status --output json

# YAML format
python -m netcommander_cli.cli status --output yaml
```

**Example Output (table):**
```
   NetCommander Status
╭────────┬───────╮
│ Outlet │ State │
├────────┼───────┤
│   1    │  ON   │
│   2    │  OFF  │
│   3    │  OFF  │
│   4    │  OFF  │
│   5    │  OFF  │
╰────────┴───────╯

Total Current: 0.15A
Temperature: XX
```

### Control Individual Outlet

```bash
# Turn outlet ON
python -m netcommander_cli.cli outlet 1 on

# Turn outlet OFF
python -m netcommander_cli.cli outlet 5 off

# Toggle outlet
python -m netcommander_cli.cli outlet 3 toggle
```

### Control All Outlets

```bash
# Turn all outlets ON
python -m netcommander_cli.cli all on

# Turn all outlets OFF
python -m netcommander_cli.cli all off
```

### Monitor in Real-Time

Watch outlet states update in real-time:

```bash
# Default 2-second interval
python -m netcommander_cli.cli monitor

# Custom interval (5 seconds)
python -m netcommander_cli.cli monitor --interval 5
```

Press `Ctrl+C` to stop monitoring.

### Show Configuration

Display current configuration:

```bash
python -m netcommander_cli.cli info
```

## Complete Examples

### Using Environment Variables

```bash
# Set up .env file
cat > .env <<EOF
NETCOMMANDER_HOST=192.168.1.100
NETCOMMANDER_USER=admin
NETCOMMANDER_PASSWORD=secret
EOF

# Commands will use .env automatically
python -m netcommander_cli.cli status
python -m netcommander_cli.cli outlet 1 on
```

### Using Command-Line Options

```bash
# Explicit parameters
python -m netcommander_cli.cli --host 192.168.1.100 --password secret status

# Turn on outlet 2
python -m netcommander_cli.cli --host 192.168.1.100 --password secret outlet 2 on
```

### Scripting

```bash
#!/bin/bash
# Restart equipment on outlet 1

HOST="192.168.1.100"
PASS="secret"

echo "Turning off outlet 1..."
python -m netcommander_cli.cli --host $HOST --password $PASS outlet 1 off

echo "Waiting 10 seconds..."
sleep 10

echo "Turning on outlet 1..."
python -m netcommander_cli.cli --host $HOST --password $PASS outlet 1 on

echo "Done!"
```

### JSON Output for Parsing

```bash
# Get JSON output
python -m netcommander_cli.cli --host 192.168.1.100 status --output json

# Parse with jq
python -m netcommander_cli.cli status --output json | jq '.outlets["1"]'

# Check if outlet 1 is on
if python -m netcommander_cli.cli status --output json | jq -e '.outlets["1"] == true' > /dev/null; then
    echo "Outlet 1 is ON"
else
    echo "Outlet 1 is OFF"
fi
```

## Error Handling

The CLI provides clear error messages:

```bash
# Authentication error
Error: Authentication failed for admin@192.168.1.100

# Connection error
Error: Cannot connect to device: 192.168.1.100

# Invalid outlet number
Error: Invalid outlet number: 6 (must be 1-5)
```

Exit codes:
- `0` - Success
- `1` - Error occurred

## Tips

1. **Use environment variables** for repeated commands
2. **JSON output** is best for scripting and automation
3. **Monitor mode** is useful for real-time troubleshooting
4. **Save credentials** in `.env` file (add to `.gitignore`!)

## Troubleshooting

### CLI not finding device

```bash
# Test connectivity
ping 192.168.1.100

# Try explicit host
python -m netcommander_cli.cli --host 192.168.1.100 status
```

### Authentication fails

```bash
# Check credentials
python -m netcommander_cli.cli info

# Try default password
python -m netcommander_cli.cli --password admin status
```

### Module not found

```bash
# Reinstall with CLI dependencies
uv pip install -e ".[cli]"

# Verify installation
python -c "import netcommander_cli; print('OK')"
```

---

**For API documentation, see `API_SPECIFICATION.md`**
