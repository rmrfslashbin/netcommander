# Development Setup

This project uses `uv` for Python environment management.

## Prerequisites

- Python 3.11+
- `uv` installed (https://github.com/astral-sh/uv)

## Setup Steps

1. **Clone and checkout the development branch:**
   ```bash
   git checkout auth-rewrite
   ```

2. **Create virtual environment with uv:**
   ```bash
   uv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   uv pip install -r requirements-dev.txt
   ```

5. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your NetCommander device credentials
   ```

## Running the Authentication Test

Once your `.env` file is configured with your device credentials:

```bash
# Make sure venv is activated
source .venv/bin/activate

# Run the auth test
python test_auth.py
```

The test will try various authentication methods and report which one works with your device.

## Development Workflow

1. **Format code:**
   ```bash
   black .
   ```

2. **Type checking:**
   ```bash
   mypy custom_components/netcommander
   ```

3. **Linting:**
   ```bash
   flake8 custom_components/netcommander
   ```

4. **Run tests:**
   ```bash
   pytest
   ```

## Installing in Home Assistant

For development testing in Home Assistant:

1. Copy the `custom_components/netcommander` folder to your HA config directory
2. Restart Home Assistant
3. Add the integration through the UI

## Using uv for Package Management

Add new dependencies:
```bash
uv pip install <package>
```

Sync with requirements file:
```bash
uv pip sync requirements-dev.txt
```

## Project Structure

```
netcommander/
├── .env                    # Your local config (gitignored)
├── .env.example           # Template for environment variables
├── .gitignore             # Git ignore rules
├── .venv/                 # Virtual environment (gitignored)
├── custom_components/     # Home Assistant integration
│   └── netcommander/
├── pyproject.toml         # Project configuration
├── requirements-dev.txt   # Development dependencies
├── test_auth.py          # Authentication testing script
└── tests/                # Unit tests
```