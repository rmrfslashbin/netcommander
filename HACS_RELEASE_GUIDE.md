# HACS Release Guide

**Complete guide for creating a new release of the NetCommander Home Assistant integration.**

This guide is designed for AI coders to perform a full release cycle autonomously, including version bumping, building, tagging, pushing, and creating GitHub releases.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Version Numbering](#version-numbering)
3. [Pre-Release Checklist](#pre-release-checklist)
4. [Automated Release (GitHub Actions)](#automated-release-github-actions) ⭐ **Recommended**
5. [Manual Release Process](#manual-release-process)
6. [Files That Need Version Updates](#files-that-need-version-updates)
7. [Automated Release Script](#automated-release-script)
8. [Post-Release Verification](#post-release-verification)
9. [Troubleshooting](#troubleshooting)

---

## Quick Reference

### Version Format
```
YYYY.MM.DD.PATCH
Example: 2025.10.16.4
```

### Files to Update
1. `pyproject.toml` - Line 3: `version = "YYYY.MM.DD.PATCH"`
2. `custom_components/netcommander/manifest.json` - Line 12: `"version": "YYYY.MM.DD.PATCH"`

### Git Operations
```bash
git add pyproject.toml custom_components/netcommander/manifest.json
git commit -m "chore: Bump version to vYYYY.MM.DD.PATCH"
git tag -a vYYYY.MM.DD.PATCH -m "Release vYYYY.MM.DD.PATCH: <description>"
git push origin main
git push origin vYYYY.MM.DD.PATCH
```

### Release Artifact
```bash
cd custom_components
zip -r ../netcommander-vYYYY.MM.DD.PATCH.zip netcommander -x "*.pyc" -x "*/__pycache__/*"
cd ..
```

### GitHub Release
```bash
gh release create vYYYY.MM.DD.PATCH \
  netcommander-vYYYY.MM.DD.PATCH.zip \
  --title "vYYYY.MM.DD.PATCH - <Title>" \
  --notes "<Release notes>"
```

---

## Version Numbering

### Format: `YYYY.MM.DD.PATCH`

- **YYYY**: 4-digit year (e.g., 2025)
- **MM**: 2-digit month with leading zero (e.g., 01, 10)
- **DD**: 2-digit day with leading zero (e.g., 05, 16)
- **PATCH**: Incremental patch number for same-day releases (0, 1, 2, 3, ...)

### Examples
```
2025.10.16.0  - First release on October 16, 2025
2025.10.16.1  - Second release on same day (bug fix)
2025.10.16.2  - Third release on same day
2025.10.17.0  - First release on next day
```

### Determining Next Version

**If releasing today:**
1. Get today's date: `date +%Y.%m.%d`
2. Check latest version: `git tag -l "v$(date +%Y.%m.%d)*" | sort -V | tail -1`
3. If no tags for today: Use `.0`
4. If tags exist: Increment last number

**Example:**
```bash
# Today is 2025-10-17
# Latest tag is v2025.10.16.4
# Next version: 2025.10.17.0

# If v2025.10.17.0 exists, use v2025.10.17.1
```

---

## Pre-Release Checklist

### 1. **Code Quality**
- [ ] All tests pass: `pytest tests/`
- [ ] No linting errors: `ruff check .`
- [ ] Code formatted: `black .`
- [ ] No type errors: `mypy src/`

### 2. **Documentation**
- [ ] README.md is up to date
- [ ] CHANGELOG or release notes prepared
- [ ] Any new features documented
- [ ] API changes documented

### 3. **Integration Files**
- [ ] `manifest.json` has correct requirements
- [ ] `strings.json` and `translations/en.json` match
- [ ] `hacs.json` is present and valid
- [ ] All entity platforms tested

### 4. **Git Status**
- [ ] Working directory clean: `git status`
- [ ] On correct branch: `git branch --show-current` (should be `main`)
- [ ] Pulled latest: `git pull origin main`

### 5. **Version Planning**
- [ ] Determine new version number
- [ ] Release notes/title prepared
- [ ] Breaking changes documented (if any)

---

## Automated Release (GitHub Actions)

### ⭐ Recommended Approach

**GitHub Actions automatically builds and releases when you push a version tag.**

### How It Works

1. **You update versions and push a tag**
2. **GitHub Actions automatically:**
   - ✅ Verifies version consistency across files
   - ✅ Builds the zip file (excluding bytecode)
   - ✅ Validates zip integrity
   - ✅ Creates GitHub release
   - ✅ Attaches zip to release
   - ✅ Generates release notes from tag annotation
   - ✅ Auto-generates changelog from commits

### Workflow File

Location: `.github/workflows/release.yaml`

Triggers on: Tags matching `v*.*.*.*` pattern (e.g., `v2025.10.17.0`)

### Usage

#### Step 1: Update Versions

```bash
# Determine new version
NEW_VERSION="2025.10.17.0"

# Update pyproject.toml
sed -i '' "s/^version = .*/version = \"${NEW_VERSION}\"/" pyproject.toml

# Update manifest.json
sed -i '' "s/\"version\": \".*\"/\"version\": \"${NEW_VERSION}\"/" custom_components/netcommander/manifest.json

# Commit
git add pyproject.toml custom_components/netcommander/manifest.json
git commit -m "chore: Bump version to v${NEW_VERSION}"
```

#### Step 2: Create Annotated Tag with Release Notes

```bash
git tag -a v2025.10.17.0 -m "$(cat <<'EOF'
# Dynamic Outlet Detection & Configurable Scan Interval

## Features
- **Dynamic Outlet Detection**: Automatically detects 5, 8, or N outlets
- **Configurable Scan Interval**: Adjust polling from 10-300 seconds via UI
- **Options Flow**: Update IP, credentials, and scan interval without re-adding

## Bug Fixes
- Fixed asyncio import location in coordinator
- Improved timeout error handling
- Synced bundled and source libraries

## Documentation
- Added AUTOMATIONS.md with 15+ examples
- Updated README for dynamic outlets
- Added configuration UI documentation

## Breaking Changes
None - fully backward compatible
EOF
)"
```

#### Step 3: Push Tag

```bash
# Push commits
git push origin main

# Push tag - THIS TRIGGERS THE WORKFLOW
git push origin v2025.10.17.0
```

#### Step 4: Monitor Workflow

```bash
# Watch the workflow run
gh run watch

# Or visit: https://github.com/rmrfslashbin/netcommander/actions
```

#### Step 5: Verify Release

Within 2-3 minutes, the release will be created automatically:
- Visit: https://github.com/rmrfslashbin/netcommander/releases
- Verify zip is attached
- Check release notes

### Advantages of GitHub Actions

✅ **Consistent** - Same build process every time
✅ **Validated** - Automatic version consistency checks
✅ **Clean** - No local bytecode or cache in zip
✅ **Fast** - 2-3 minutes from push to release
✅ **Auditable** - All builds logged and reproducible
✅ **Hands-off** - No manual zip building or uploading

### What the Workflow Does

```yaml
1. Version Verification
   - Checks pyproject.toml version matches tag
   - Checks manifest.json version matches tag
   - Fails if versions don't match

2. Build Artifact
   - Creates zip excluding:
     ✗ __pycache__ directories
     ✗ .pyc/.pyo files
     ✗ .DS_Store files
   - Verifies zip integrity
   - Checks no bytecode leaked into zip

3. Create Release
   - Uses tag annotation as primary release notes
   - Adds installation instructions
   - Adds links to changelog, docs, issues
   - Auto-generates commit-based changelog
   - Attaches zip file

4. Verification
   - Prints success summary
   - Shows release URL
   - Notes HACS detection time (1-2 hours)
```

### For AI Coders: Autonomous Release

```python
# Complete autonomous release with GitHub Actions

def create_release_with_github_actions(new_version: str, description: str):
    """
    Create a new release using GitHub Actions automation.

    Args:
        new_version: Version like "2025.10.17.0" (without 'v' prefix)
        description: Multiline release notes
    """

    # 1. Update version files
    update_pyproject_version(new_version)
    update_manifest_version(new_version)

    # 2. Commit version bump
    run(["git", "add", "pyproject.toml",
         "custom_components/netcommander/manifest.json"])
    run(["git", "commit", "-m", f"chore: Bump version to v{new_version}"])

    # 3. Create annotated tag with release notes
    run(["git", "tag", "-a", f"v{new_version}", "-m", description])

    # 4. Push (this triggers GitHub Actions)
    run(["git", "push", "origin", "main"])
    run(["git", "push", "origin", f"v{new_version}"])

    # 5. Wait for workflow to complete
    print("⏳ Waiting for GitHub Actions to build and release...")
    run(["gh", "run", "watch"])

    # 6. Verify release created
    print(f"✅ Release complete!")
    print(f"🔗 https://github.com/rmrfslashbin/netcommander/releases/tag/v{new_version}")

    return True
```

**That's it!** No manual zip building, no release creation - GitHub Actions handles everything.

---

## Manual Release Process

### Step 1: Determine New Version

```bash
# Get today's date in version format
TODAY=$(date +%Y.%m.%d)
echo "Today: $TODAY"

# Check for existing tags today
LATEST_TAG=$(git tag -l "v${TODAY}*" | sort -V | tail -1)

if [ -z "$LATEST_TAG" ]; then
    # No release today yet
    NEW_VERSION="${TODAY}.0"
else
    # Extract patch number and increment
    PATCH=$(echo $LATEST_TAG | cut -d. -f4)
    NEW_PATCH=$((PATCH + 1))
    NEW_VERSION="${TODAY}.${NEW_PATCH}"
fi

echo "New version: $NEW_VERSION"
```

### Step 2: Update Version in Files

**File 1: `pyproject.toml`**

Location: Line 3

```python
# Before
version = "2025.10.16.4"

# After
version = "2025.10.17.0"
```

**File 2: `custom_components/netcommander/manifest.json`**

Location: Line 12 (look for `"version":`)

```json
// Before
"version": "2025.10.16.4"

// After
"version": "2025.10.17.0"
```

### Step 3: Commit Version Bump

```bash
# Stage version files
git add pyproject.toml custom_components/netcommander/manifest.json

# Commit with clear message
git commit -m "chore: Bump version to v2025.10.17.0"
```

### Step 4: Create Git Tag

```bash
# Create annotated tag with release description
git tag -a v2025.10.17.0 -m "$(cat <<'EOF'
Release v2025.10.17.0: <Short Title>

Changes:
- Feature: <description>
- Fix: <description>
- Docs: <description>

Full changelog: https://github.com/rmrfslashbin/netcommander/releases/tag/v2025.10.17.0
EOF
)"
```

### Step 5: Push to GitHub

```bash
# Push commit
git push origin main

# Push tag
git push origin v2025.10.17.0
```

### Step 6: Build Release Artifact

```bash
# Navigate to custom_components directory
cd custom_components

# Create zip WITHOUT bytecode or cache files
zip -r ../netcommander-v2025.10.17.0.zip netcommander \
  -x "*.pyc" \
  -x "*/__pycache__/*" \
  -x "*.pyo" \
  -x "*/.DS_Store"

# Return to root
cd ..

# Verify zip contents
unzip -l netcommander-v2025.10.17.0.zip | head -20
```

**Important:** The zip MUST NOT contain:
- `__pycache__/` directories
- `.pyc` or `.pyo` files
- `.DS_Store` files
- Any IDE-specific files

### Step 7: Create GitHub Release

```bash
gh release create v2025.10.17.0 \
  netcommander-v2025.10.17.0.zip \
  --title "v2025.10.17.0 - <Descriptive Title>" \
  --notes "$(cat <<'EOF'
# Release v2025.10.17.0

## 🎉 What's New

### Features
- **Dynamic Outlet Detection**: Automatically detects outlet count
- **Configurable Scan Interval**: Adjust polling from 10-300 seconds

### Bug Fixes
- Fixed timeout error handling
- Improved connection stability

### Documentation
- Added AUTOMATIONS.md with 15+ examples
- Updated README with new features

## 📦 Installation

### Via HACS (Recommended)
1. Go to HACS → Integrations
2. Find "Synaccess NetCommander"
3. Click "Update" (or "Download" if new)
4. Restart Home Assistant

### Manual Installation
1. Download `netcommander-v2025.10.17.0.zip`
2. Extract to `custom_components/netcommander/`
3. Restart Home Assistant

## 🔗 Links
- [Full Changelog](https://github.com/rmrfslashbin/netcommander/compare/v2025.10.16.4...v2025.10.17.0)
- [Documentation](https://github.com/rmrfslashbin/netcommander#readme)
- [Report Issues](https://github.com/rmrfslashbin/netcommander/issues)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### Step 8: Verify Release

1. Check GitHub releases page: https://github.com/rmrfslashbin/netcommander/releases
2. Verify zip file is attached
3. Verify release notes are formatted correctly
4. Test download link works

---

## Files That Need Version Updates

### Critical Files (Must Update)

#### 1. `pyproject.toml`
**Location:** Line 3
**Format:** `version = "YYYY.MM.DD.PATCH"`

```toml
[project]
name = "netcommander"
version = "2025.10.17.0"  # ← UPDATE THIS
description = "Home Assistant custom component..."
```

#### 2. `custom_components/netcommander/manifest.json`
**Location:** Line 12
**Format:** `"version": "YYYY.MM.DD.PATCH"`

```json
{
  "domain": "netcommander",
  "name": "Synaccess NetCommander",
  ...
  "version": "2025.10.17.0"  // ← UPDATE THIS
}
```

### Optional Files (Auto-Generated)

These files are automatically created and don't need version updates:

- `netcommander-vYYYY.MM.DD.PATCH.zip` - Created during build
- Git tags - Created with `git tag`
- GitHub releases - Created with `gh release create`

---

## Automated Release Script

### Full Autonomous Release

Save this as `scripts/release.sh`:

```bash
#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}NetCommander Release Script${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check we're on main branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
    echo -e "${RED}Error: Must be on main branch (currently on $BRANCH)${NC}"
    exit 1
fi

# Check working directory is clean
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}Error: Working directory not clean. Commit changes first.${NC}"
    git status
    exit 1
fi

# Pull latest
echo -e "${YELLOW}Pulling latest from origin...${NC}"
git pull origin main

# Determine new version
TODAY=$(date +%Y.%m.%d)
LATEST_TAG=$(git tag -l "v${TODAY}*" | sort -V | tail -1)

if [ -z "$LATEST_TAG" ]; then
    NEW_VERSION="${TODAY}.0"
else
    PATCH=$(echo $LATEST_TAG | cut -d. -f4)
    NEW_PATCH=$((PATCH + 1))
    NEW_VERSION="${TODAY}.${NEW_PATCH}"
fi

echo -e "${GREEN}New version: ${NEW_VERSION}${NC}\n"

# Prompt for release title and notes
read -p "Release title: " RELEASE_TITLE
read -p "Release notes file (or press Enter to use editor): " NOTES_FILE

if [ -z "$NOTES_FILE" ]; then
    # Open editor for notes
    NOTES_FILE=$(mktemp)
    ${EDITOR:-vim} "$NOTES_FILE"
fi

RELEASE_NOTES=$(cat "$NOTES_FILE")

# Update pyproject.toml
echo -e "${YELLOW}Updating pyproject.toml...${NC}"
sed -i.bak "s/^version = .*/version = \"${NEW_VERSION}\"/" pyproject.toml
rm pyproject.toml.bak

# Update manifest.json
echo -e "${YELLOW}Updating manifest.json...${NC}"
sed -i.bak "s/\"version\": \".*\"/\"version\": \"${NEW_VERSION}\"/" custom_components/netcommander/manifest.json
rm custom_components/netcommander/manifest.json.bak

# Commit version bump
echo -e "${YELLOW}Committing version bump...${NC}"
git add pyproject.toml custom_components/netcommander/manifest.json
git commit -m "chore: Bump version to v${NEW_VERSION}"

# Create tag
echo -e "${YELLOW}Creating git tag...${NC}"
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}: ${RELEASE_TITLE}"

# Push
echo -e "${YELLOW}Pushing to GitHub...${NC}"
git push origin main
git push origin "v${NEW_VERSION}"

# Build zip
echo -e "${YELLOW}Building release zip...${NC}"
cd custom_components
zip -r "../netcommander-v${NEW_VERSION}.zip" netcommander \
  -x "*.pyc" \
  -x "*/__pycache__/*" \
  -x "*.pyo" \
  -x "*/.DS_Store"
cd ..

# Create GitHub release
echo -e "${YELLOW}Creating GitHub release...${NC}"
gh release create "v${NEW_VERSION}" \
  "netcommander-v${NEW_VERSION}.zip" \
  --title "v${NEW_VERSION} - ${RELEASE_TITLE}" \
  --notes "${RELEASE_NOTES}"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Release v${NEW_VERSION} completed!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo "Release URL: https://github.com/rmrfslashbin/netcommander/releases/tag/v${NEW_VERSION}"
```

**Usage:**
```bash
chmod +x scripts/release.sh
./scripts/release.sh
```

---

## Post-Release Verification

### Immediate Checks

1. **GitHub Release Page**
   - Visit: https://github.com/rmrfslashbin/netcommander/releases
   - Verify release appears
   - Check zip file is attached
   - Verify release notes render correctly

2. **Git Tags**
   ```bash
   git tag -l "v*" | sort -V | tail -5
   # Should show your new tag
   ```

3. **Zip File Integrity**
   ```bash
   unzip -t netcommander-vYYYY.MM.DD.PATCH.zip
   # Should report no errors
   ```

4. **Version Consistency**
   ```bash
   # Check pyproject.toml
   grep "^version = " pyproject.toml

   # Check manifest.json
   grep '"version":' custom_components/netcommander/manifest.json

   # Both should show same version
   ```

### HACS Verification

**Within 1-2 hours:**
1. Go to HACS in Home Assistant
2. Navigate to Integrations
3. Search for "NetCommander"
4. Verify new version shows as available
5. Test update process

**If version doesn't appear:**
- HACS caches repository data (can take up to 2 hours)
- Check `hacs.json` is valid
- Verify tag is pushed: `git ls-remote --tags origin`

### User Testing

1. Install in test Home Assistant instance
2. Verify all entities created correctly
3. Test switch on/off
4. Test button reboot
5. Check sensor values
6. Verify logs for errors

---

## Troubleshooting

### Issue: "Version already exists"

**Problem:** Git tag or GitHub release already exists for this version

**Solution:**
```bash
# Delete local tag
git tag -d vYYYY.MM.DD.PATCH

# Delete remote tag
git push origin :refs/tags/vYYYY.MM.DD.PATCH

# Delete GitHub release (if created)
gh release delete vYYYY.MM.DD.PATCH

# Start over with new version number
```

### Issue: "Zip contains __pycache__"

**Problem:** Python bytecode included in zip

**Solution:**
```bash
# Delete bad zip
rm netcommander-vYYYY.MM.DD.PATCH.zip

# Clean all pycache
find custom_components/netcommander -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find custom_components/netcommander -name "*.pyc" -delete

# Rebuild zip with explicit excludes
cd custom_components
zip -r ../netcommander-vYYYY.MM.DD.PATCH.zip netcommander \
  -x "*.pyc" -x "*/__pycache__/*"
cd ..

# Upload corrected zip to GitHub release
gh release upload vYYYY.MM.DD.PATCH netcommander-vYYYY.MM.DD.PATCH.zip --clobber
```

### Issue: "HACS not showing update"

**Problem:** HACS hasn't refreshed repository cache

**Solutions:**
1. **Wait 2 hours** - HACS caches repository data
2. **Force refresh:**
   - HACS → Three dots → Custom repositories
   - Remove NetCommander
   - Re-add NetCommander
   - Restart Home Assistant

3. **Check tag format:**
   ```bash
   git tag -l
   # Tags MUST start with 'v' (v2025.10.17.0, not 2025.10.17.0)
   ```

4. **Verify manifest.json:**
   ```bash
   cat custom_components/netcommander/manifest.json | grep version
   # Must match git tag version
   ```

### Issue: "Working directory not clean"

**Problem:** Uncommitted changes in repository

**Solution:**
```bash
# Check what's modified
git status

# Either commit changes
git add <files>
git commit -m "description"

# Or stash temporarily
git stash
# ... do release ...
git stash pop
```

### Issue: "gh: command not found"

**Problem:** GitHub CLI not installed

**Solution:**
```bash
# macOS
brew install gh

# Linux
# See: https://github.com/cli/cli/blob/trunk/docs/install_linux.md

# Authenticate
gh auth login
```

**Manual alternative:**
1. Go to https://github.com/rmrfslashbin/netcommander/releases/new
2. Choose tag: vYYYY.MM.DD.PATCH
3. Set title: "vYYYY.MM.DD.PATCH - <Title>"
4. Add release notes
5. Upload zip file
6. Click "Publish release"

---

## AI Coder Autonomous Release Procedure

**For AI coders performing autonomous releases:**

### Input Required from User
1. Confirmation to proceed with release
2. (Optional) Release title/description

### Autonomous Steps

```python
# 1. Determine new version
import datetime
today = datetime.date.today()
base_version = today.strftime("%Y.%m.%d")

# Check existing tags for today
existing = subprocess.run(
    ["git", "tag", "-l", f"v{base_version}*"],
    capture_output=True, text=True
).stdout.strip().split('\n')

if existing == ['']:
    patch = 0
else:
    patches = [int(t.split('.')[-1]) for t in existing]
    patch = max(patches) + 1

new_version = f"{base_version}.{patch}"

# 2. Update version files
update_file("pyproject.toml", line=3, pattern=r'version = ".*"',
            replacement=f'version = "{new_version}"')

update_file("custom_components/netcommander/manifest.json",
            pattern=r'"version": ".*"',
            replacement=f'"version": "{new_version}"')

# 3. Git operations
run_command(["git", "add", "pyproject.toml",
             "custom_components/netcommander/manifest.json"])
run_command(["git", "commit", "-m", f"chore: Bump version to v{new_version}"])
run_command(["git", "tag", "-a", f"v{new_version}",
             "-m", f"Release v{new_version}: {description}"])
run_command(["git", "push", "origin", "main"])
run_command(["git", "push", "origin", f"v{new_version}"])

# 4. Build zip
os.chdir("custom_components")
run_command(["zip", "-r", f"../netcommander-v{new_version}.zip", "netcommander",
             "-x", "*.pyc", "-x", "*/__pycache__/*"])
os.chdir("..")

# 5. Create GitHub release
run_command(["gh", "release", "create", f"v{new_version}",
             f"netcommander-v{new_version}.zip",
             "--title", f"v{new_version} - {title}",
             "--notes", release_notes])

print(f"✅ Release v{new_version} completed!")
print(f"URL: https://github.com/rmrfslashbin/netcommander/releases/tag/v{new_version}")
```

---

## Summary

**To create a release:**

1. ✅ Verify tests pass and code is clean
2. ✅ Determine new version: `YYYY.MM.DD.PATCH`
3. ✅ Update `pyproject.toml` line 3
4. ✅ Update `manifest.json` line 12
5. ✅ Commit: `git commit -m "chore: Bump version to vX.X.X.X"`
6. ✅ Tag: `git tag -a vX.X.X.X -m "Release vX.X.X.X: <desc>"`
7. ✅ Push: `git push origin main && git push origin vX.X.X.X`
8. ✅ Build: `cd custom_components && zip -r ../netcommander-vX.X.X.X.zip netcommander -x "*.pyc" -x "*/__pycache__/*" && cd ..`
9. ✅ Release: `gh release create vX.X.X.X netcommander-vX.X.X.X.zip --title "..." --notes "..."`
10. ✅ Verify on GitHub

**Done!** HACS will pick up the new release within 1-2 hours.

---

**Questions? Issues?**
- GitHub Issues: https://github.com/rmrfslashbin/netcommander/issues
- Author: Robert Sigler (code@sigler.io)
