# Contributing to NetCommander

Thank you for your interest in contributing to the NetCommander project! This document provides guidelines for contributing.

## 🎯 Ways to Contribute

### 1. **Device Compatibility Testing**
The most valuable contribution right now!

- Test with your Synaccess device (especially non-5-outlet models)
- Report compatibility results
- Share device info (model, firmware, outlet count)
- Document any quirks or special behavior

**How to report:**
```bash
# Get your device info
python -m netcommander_cli.cli --host YOUR_IP --password YOUR_PASSWORD info

# Create an issue with the output
```

### 2. **Bug Reports**
Found a bug? Please report it!

**Before submitting:**
- Check existing issues to avoid duplicates
- Test with the latest version
- Gather relevant information (logs, device model, HA version)

**Issue template:**
```markdown
**Description:**
Brief description of the bug

**Environment:**
- NetCommander version:
- Home Assistant version:
- Device model:
- Python version:

**Steps to reproduce:**
1.
2.
3.

**Expected behavior:**


**Actual behavior:**


**Logs:**
```
Paste relevant logs here
```
```

### 3. **Feature Requests**
Have an idea? We'd love to hear it!

**Good feature requests include:**
- Clear description of the feature
- Use case / why it's useful
- Examples of how it would work
- Consideration of edge cases

### 4. **Code Contributions**
Want to submit code? Awesome!

## 🔧 Development Setup

### Clone and Setup
```bash
git clone https://github.com/rmrfslashbin/netcommander.git
cd netcommander
uv venv && source .venv/bin/activate
uv pip install -e ".[cli,ha,dev]"
```

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/netcommander --cov=custom_components/netcommander

# Run specific test file
pytest tests/test_client.py

# Run integration tests
pytest -m integration
```

### Code Quality
```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy src/
```

## 📝 Pull Request Process

### 1. **Fork and Branch**
```bash
# Fork the repo on GitHub
git clone https://github.com/YOUR_USERNAME/netcommander.git
cd netcommander

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. **Make Your Changes**
- Write clean, readable code
- Follow existing code style
- Add tests for new functionality
- Update documentation if needed

### 3. **Test Your Changes**
```bash
# Run tests
pytest

# Run linters
black .
ruff check .

# Test manually
python -m netcommander_cli.cli --host YOUR_IP info
```

### 4. **Commit Your Changes**
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add support for 8-outlet devices"
# or
git commit -m "fix: Correct timeout handling in status polling"
# or
git commit -m "docs: Update README with new features"
```

**Commit message format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `chore:` - Maintenance tasks
- `refactor:` - Code refactoring

### 5. **Push and Create PR**
```bash
# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub
# - Provide clear description
# - Reference related issues
# - Include test results
```

### 6. **PR Review Process**
- Maintainer will review your PR
- Address any requested changes
- Once approved, PR will be merged
- Your contribution will be credited in release notes!

## 🧪 Testing Guidelines

### Test Coverage
- Aim for >80% coverage for new code
- Test both success and failure cases
- Test edge cases and boundary conditions

### Test Types
1. **Unit Tests** - Test individual functions/methods
2. **Integration Tests** - Test component interactions
3. **Manual Tests** - Test with real device

### Writing Tests
```python
import pytest
from netcommander import NetCommanderClient

@pytest.mark.asyncio
async def test_get_status():
    """Test status retrieval."""
    async with NetCommanderClient("192.168.1.100", "admin", "password") as client:
        status = await client.get_status()
        assert status.outlets is not None
        assert len(status.outlets) > 0
```

## 📚 Documentation Guidelines

### When to Update Docs
- Adding new features
- Changing behavior
- Adding configuration options
- Creating new automations

### Documentation Files
- **README.md** - Overview and quick start
- **AUTOMATIONS.md** - Automation examples
- **API_SPECIFICATION.md** - API details
- **INSTALLATION.md** - Detailed setup
- **CHANGELOG.md** - Version history

### Documentation Style
- Use clear, concise language
- Include code examples
- Show expected output
- Explain the "why" not just the "how"

## 🐛 Debugging Tips

### Enable Debug Logging (Home Assistant)
```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.netcommander: debug
```

### CLI Debugging
```bash
# Use verbose output
python -m netcommander_cli.cli --host IP info --output json

# Check connectivity
curl http://YOUR_IP/cmd.cgi?$A5
```

### Common Issues
1. **Import errors** - Check sys.path and bundled library structure
2. **Timeout errors** - Verify network connectivity and device responsiveness
3. **Parsing errors** - Check device response format matches expectations

## 🔒 Security

### Reporting Security Issues
**Do not** open public issues for security vulnerabilities.

Instead:
- Email: code@sigler.io
- Subject: "NetCommander Security Issue"
- Provide details, impact, and reproduction steps
- Allow time for fix before public disclosure

### Security Best Practices
- Never commit passwords or credentials
- Use `.env` files for local development
- Keep dependencies updated
- Validate user input
- Handle errors gracefully

## 📋 Code Style Guidelines

### Python Style
- Follow PEP 8
- Use type hints where possible
- Maximum line length: 88 (Black default)
- Use async/await for I/O operations
- Use Pydantic for data models

### Example
```python
from typing import Optional
from pydantic import BaseModel

class DeviceInfo(BaseModel):
    """Device information model."""
    model: str
    firmware_version: Optional[str] = None

    async def get_status(self) -> dict:
        """Retrieve device status."""
        # Implementation
        pass
```

### Home Assistant Style
- Follow HA development guidelines
- Use DataUpdateCoordinator for polling
- Implement proper entity platforms
- Handle exceptions appropriately

## 🎉 Recognition

Contributors will be:
- Listed in release notes
- Credited in git commits (Co-Authored-By)
- Mentioned in README (for significant contributions)
- Given a shout-out on social media

## ❓ Questions?

- **General questions**: Open a GitHub Discussion
- **Bug reports**: Open a GitHub Issue
- **Feature ideas**: Open a GitHub Issue
- **Direct contact**: code@sigler.io

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to NetCommander!** 🚀

Every contribution, no matter how small, helps make this project better for the Home Assistant community.
