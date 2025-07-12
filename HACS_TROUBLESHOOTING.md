# HACS Troubleshooting Guide

If HACS can't see the integration, try these steps:

## 1. Repository URL Format

Make sure you're using the exact format in HACS:

```
Repository: rmrfslashbin/netcommander
Category: Integration
```

**NOT:**
- `https://github.com/rmrfslashbin/netcommander`
- `github.com/rmrfslashbin/netcommander` 
- `rmrfslashbin/netcommander.git`

## 2. Clear HACS Cache

1. Go to **HACS** → **Integrations**
2. Click the **three dots menu** (⋮) in top right
3. Select **Reload**
4. Wait a few minutes and try again

## 3. Check Repository Status

1. Verify the repository is public: https://github.com/rmrfslashbin/netcommander
2. Check the latest commit shows our integration files
3. Ensure `custom_components/netcommander/` folder exists

## 4. Manual Validation

You can manually validate the structure:

```bash
# Check required files exist
ls custom_components/netcommander/
# Should show: __init__.py, manifest.json, hacs.json, etc.

# Check manifest.json format
cat custom_components/netcommander/manifest.json
# Should be valid JSON with version 2.0.1
```

## 5. Alternative: Manual Installation

If HACS still doesn't work, you can install manually:

1. Download the latest release: https://github.com/rmrfslashbin/netcommander/releases
2. Extract `custom_components/netcommander/` to your HA config
3. Restart Home Assistant
4. Add integration normally

## 6. HACS Debug

Enable HACS debug logging:

```yaml
# configuration.yaml
logger:
  logs:
    custom_components.hacs: debug
```

Then check logs for any validation errors.

## 7. Wait Period

Sometimes HACS needs time to process new repositories. Try waiting 10-15 minutes after adding the repository before expecting it to appear in the integration list.

## 8. Repository Requirements Checklist

Our repository has:
- ✅ `custom_components/netcommander/` directory
- ✅ `manifest.json` with proper version
- ✅ `hacs.json` with metadata  
- ✅ `__init__.py` with async_setup_entry
- ✅ `info.md` for HACS description
- ✅ Public repository
- ✅ Valid Python integration structure

If none of these solve the issue, please create an issue on the repository with:
- Your HACS version
- Home Assistant version  
- Screenshots of the error
- Any relevant logs