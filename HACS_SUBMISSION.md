# HACS Submission Checklist

This document tracks compliance with HACS requirements for publishing the Synaccess NetCommander integration.

## ✅ Repository Requirements

### General
- [x] **Public GitHub repository**
- [x] **Repository description**: Clear description of PDU control integration
- [x] **Repository topics**: 16 relevant topics including `hacs`, `home-assistant`, `integration`, `pdu`, `power-control`, etc.
- [x] **README.md**: Comprehensive documentation with installation, usage, and examples

### Structure
- [x] **Single integration**: Only one subdirectory in `custom_components/`
- [x] **Correct placement**: All files in `custom_components/netcommander/`
- [x] **No root __init__.py**: Removed `custom_components/__init__.py` (HACS requirement)

## ✅ manifest.json Requirements

Location: `custom_components/netcommander/manifest.json`

Required fields (all present):
- [x] `domain`: "netcommander"
- [x] `name`: "Synaccess NetCommander"
- [x] `documentation`: Points to GitHub repo
- [x] `issue_tracker`: Points to GitHub issues
- [x] `codeowners`: [@rmrfslashbin]
- [x] `version`: "2025.12.4"

Additional fields:
- [x] `config_flow`: true
- [x] `iot_class`: "local_polling"
- [x] `integration_type`: "device"
- [x] `requirements`: aiohttp, pydantic

## ✅ hacs.json Configuration

Location: `hacs.json` (repository root)

```json
{
  "name": "Synaccess NetCommander",
  "render_readme": true,
  "homeassistant": "2024.1.0"
}
```

- [x] `name`: Display name for HACS UI
- [x] `render_readme`: Enabled for documentation
- [x] `homeassistant`: Minimum HA version specified

## ✅ README.md Content

Comprehensive documentation including:
- [x] **Badges**: HACS, release, license
- [x] **Description**: Clear project overview
- [x] **Features**: Detailed feature list
- [x] **Supported devices**: Tested and compatible devices
- [x] **Installation**: Step-by-step HACS and CLI installation
- [x] **Configuration**: UI configuration instructions
- [x] **Usage examples**: Home Assistant and API examples
- [x] **Troubleshooting**: Common issues and solutions
- [x] **Architecture**: System design diagram
- [x] **Development**: Setup and contribution guidelines
- [x] **License**: MIT license referenced

## ✅ GitHub Releases

- [x] **Releases enabled**: Using semantic versioning (v2025.12.4)
- [x] **Automated releases**: GitHub Actions workflow configured
- [x] **Release assets**: Zip files automatically attached
- [x] **Release notes**: Auto-generated from commit messages

## ✅ Additional Best Practices

### Validation
- [x] **HACS Action**: `.github/workflows/hacs.yaml` validates on push
- [x] **Hassfest**: `.github/workflows/hassfest.yaml` validates manifest
- [x] **Release workflow**: `.github/workflows/release.yaml` automates releases

### Code Quality
- [x] **Pre-commit hooks**: Configured with black, ruff, isort
- [x] **Type hints**: Throughout codebase
- [x] **Exception handling**: Custom exception hierarchy
- [x] **Async/await**: Proper async patterns
- [x] **Coordinator pattern**: Standard HA data coordinator

### Documentation
- [x] **CHANGELOG.md**: Version history
- [x] **CONTRIBUTING.md**: Contribution guidelines
- [x] **LICENSE**: MIT license file
- [x] **Additional docs**: AUTOMATION.md, TESTING.md, etc.

### Testing
- [x] **Test suite**: Comprehensive pytest tests
- [x] **Test coverage**: HTML and terminal reports
- [x] **CI integration**: Tests can run in CI

## 📋 Home Assistant Brands (Optional but Recommended)

To fully comply with UI standards, the integration should be added to [home-assistant/brands](https://github.com/home-assistant/brands).

**Status**: ⏳ Pending submission to brands repository

This involves:
1. Creating a pull request to home-assistant/brands
2. Adding integration logo/icon
3. Providing brand information

## 🎯 HACS Default Repository Submission

**Status**: ✅ Ready for submission

The integration meets all requirements for submission to the HACS default repository:
1. All technical requirements met
2. Documentation complete
3. Active releases and versioning
4. Validation workflows passing

### To Submit:
1. Go to https://github.com/hacs/default
2. Create a new issue using the "Add integration" template
3. Provide repository URL: https://github.com/rmrfslashbin/netcommander
4. Wait for HACS team review

### Alternative (Custom Repository):
Users can add as a custom repository immediately:
1. HACS → Integrations → ⋮ (menu) → Custom repositories
2. Add URL: `https://github.com/rmrfslashbin/netcommander`
3. Category: Integration
4. Click "Add"

## 📚 References

- [HACS Integration Publishing](https://hacs.xyz/docs/publish/integration/)
- [HACS General Publishing](https://www.hacs.xyz/docs/publish/start/)
- [Home Assistant Integration Development](https://developers.home-assistant.io/docs/creating_integration_manifest/)

## ✅ Final Status

**All HACS requirements met!** ✨

The integration is ready for:
- ✅ Use as a HACS custom repository (works now)
- ✅ Submission to HACS default repository (optional)
- ⏳ Submission to home-assistant/brands (recommended for UI polish)

Version: 2025.12.4
Last Updated: 2025-12-03
