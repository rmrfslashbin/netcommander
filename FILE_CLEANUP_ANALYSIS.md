# File Cleanup Analysis

This document provides a comprehensive analysis of files in the repository that may be candidates for deletion or archival.

## Files to Delete (Recommended)

### Old Release Zips (7 files)
These are outdated release artifacts that should be removed from the repository. Releases should only exist in GitHub Releases, not in the repository itself.

**Delete:**
- `netcommander-v2025.10.15.2.zip`
- `netcommander-v2025.10.15.3.zip`
- `netcommander-v2025.10.16.zip`
- `netcommander-v2025.10.16.1.zip`
- `netcommander-v2025.10.16.2.zip`
- `netcommander-v2025.10.16.3.zip`
- `netcommander-v2025.10.16.4.zip` ← Current release, but should only live in GitHub Releases

**Rationale:** GitHub Releases handles distribution. Having zips in the repo bloats the repository size and creates confusion about which version is current.

**Action:** `rm netcommander-v*.zip`

---

### Development Test Scripts (Multiple files)
These appear to be one-off exploration/debugging scripts created during development. Most are superseded by the formal test suite in `tests/`.

**Consider Deleting:**
- `test_ha_loading.py` - One-off test for HA loading (functionality now verified)
- `test_command_formats.py` - Development exploration script
- `test_comprehensive_mapping.py` - Outlet mapping exploration
- `test_correct_syntax.py` - Syntax verification script
- `test_device_capabilities.py` - Device capability exploration
- `test_device_discovery.py` - Discovery exploration
- `test_device_info_api.py` - API info exploration
- `test_device_info.py` - Device info extraction script
- `test_explicit_commands.py` - Command testing script
- `test_inverted_logic.py` - Logic testing from debugging
- `test_outlet_toggle.py` - Toggle testing script
- `test_post_reset_verification.py` - Post-reset verification script
- `test_api_client.py` - API client testing (superseded by tests/test_client.py)
- `test_config_flow_import.py` - Config flow import testing

**Keep:**
- `tests/` directory - Formal test suite using pytest
- `tests/test_client.py` - Comprehensive client tests
- `tests/test_ha_config_flow.py` - HA integration tests
- `tests/test_ha_coordinator.py` - Coordinator tests
- `tests/test_integration.py` - Integration tests
- `tests/test_models.py` - Model tests

**Rationale:** The formal test suite in `tests/` provides comprehensive coverage. These one-off scripts were useful during development but are no longer needed. They create clutter and confusion about which tests are authoritative.

**Estimated space saved:** ~50KB of code

**Action:**
```bash
rm test_*.py
```

---

### JSON Output Files
Appears to be test output data from mapping experiments.

**Consider Deleting:**
- `outlet_mapping_results_20251015_131625.json` - Historical test data

**Rationale:** Test output data shouldn't be committed to the repository. If needed for reference, it can be regenerated.

**Action:** `rm outlet_mapping_results_*.json`

---

## Files to Keep (Important)

### Documentation Files
**Keep all of these** - they provide valuable reference and user guidance:
- `README.md` - Main project documentation ✅
- `API_SPECIFICATION.md` - API reference
- `CLI_USAGE.md` - CLI documentation
- `DEFINITIVE_MAPPING.md` - Outlet mapping reference
- `DEPLOYMENT.md` - Deployment guide
- `FACTORY_RESET_GUIDE.md` - User troubleshooting
- `INSTALLATION.md` - Installation instructions
- `INTEGRATION_SUMMARY.md` - Integration overview
- `OUTLET_MAPPING.md` - Outlet behavior documentation
- `RELEASE_CHECKLIST.md` - Release process
- `TESTING.md` - Testing documentation
- `doc/ttyACM.md` - Serial port documentation

### Core Code
**Keep all of these** - active codebase:
- `src/netcommander/` - Shared API library ✅
- `custom_components/netcommander/` - Home Assistant integration ✅
- `netcommander_cli/` - CLI tool ✅
- `tests/` - Formal test suite ✅

### Configuration Files
**Keep all of these** - project configuration:
- `pyproject.toml` - Python project configuration ✅
- `.github/workflows/` - CI/CD workflows ✅
- `.gitignore` - Git ignore rules ✅

### Test Infrastructure
**Keep:**
- `tests/__init__.py` ✅
- `tests/conftest.py` ✅

---

## Potentially Redundant Documentation

Some documentation files may have overlapping content:

### Possible Consolidation Candidates:
1. **API_SPECIFICATION.md** vs device command section in README
   - Could potentially consolidate into README or move to docs/ folder

2. **CLI_USAGE.md** vs CLI section in README
   - Could potentially consolidate, but detailed CLI docs are valuable

3. **OUTLET_MAPPING.md** + **DEFINITIVE_MAPPING.md**
   - These might cover similar ground and could be consolidated

4. **INSTALLATION.md** vs Quick Start in README
   - Could consolidate basic setup, keep INSTALLATION.md for troubleshooting

**Recommendation:** Keep separate for now. Having detailed docs is better than missing information.

---

## htmlcov/ Directory

The `htmlcov/` directory appears to contain HTML coverage reports:
- `htmlcov/status.json`

**Recommendation:** This should already be covered by `.gitignore` (htmlcov/ is listed). Verify it's not tracked.

**Action:** Confirm it's properly gitignored:
```bash
git check-ignore htmlcov/
```

---

## Summary

### Safe to Delete (12-14 files, ~50-100KB):
```bash
# Release zips
rm netcommander-v*.zip

# Development test scripts
rm test_*.py

# Test output data
rm outlet_mapping_results_*.json
```

### Keep Everything Else
The documentation is comprehensive and valuable. The core code is well-organized.

### Git Operations:
```bash
# If these files are tracked, remove from git
git rm netcommander-v*.zip
git rm test_*.py  # except files in tests/
git rm outlet_mapping_results_*.json

# Commit cleanup
git commit -m "chore: Remove old release artifacts and development test scripts"
```

---

## Updated Repository Structure (After Cleanup)

```
netcommander/
├── .github/workflows/        # CI/CD
├── custom_components/        # HA integration
├── src/netcommander/         # API library
├── netcommander_cli/         # CLI tool
├── tests/                    # Formal test suite ✅
├── doc/                      # Additional docs
├── *.md                      # Documentation files
├── pyproject.toml            # Project config
└── .gitignore                # Git ignore (updated)
```

**Result:** Cleaner repository focused on production code, formal tests, and comprehensive documentation.
