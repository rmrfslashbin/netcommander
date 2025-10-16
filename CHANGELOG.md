# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2025.10.16.4] - 2025-10-16

### Added
- **Dynamic outlet detection**: Integration automatically detects device outlet count (5, 8, or other configurations)
- **Configurable scan interval**: Users can adjust polling frequency from 10-300 seconds via Options Flow
- **Options Flow UI**: Reconfigure IP address, credentials, and scan interval without removing integration
- **Comprehensive automation examples**: New AUTOMATIONS.md with 15+ ready-to-use examples
- **Documentation updates**: Enhanced README with dynamic detection features and configuration instructions

### Changed
- Outlet entities now created dynamically based on device response (no hardcoded 5-outlet assumption)
- Switch and button platforms detect outlet count automatically
- Status parsing now determines outlet count from device response length
- Models updated to support variable outlet counts with dynamic validation
- Client methods remove hardcoded outlet validation for flexibility

### Fixed
- asyncio import moved to module level in coordinator.py
- Timeout errors now properly caught and displayed with clear messages
- Synced timeout handling between bundled and source libraries

### Deprecated
- `NUM_OUTLETS` and `OUTLET_RANGE` constants (kept for backward compatibility)
- `get_status_position()` function (use dynamic calculation instead)

### Documentation
- Added AUTOMATIONS.md with comprehensive automation examples
- Added FILE_CLEANUP_ANALYSIS.md for repository maintenance
- Updated README with dynamic outlet detection and scan interval documentation
- Updated .gitignore to prevent test artifacts and release zips

## [2025.10.16.3] - 2025-10-16

### Fixed
- Removed device tracker connection to prevent "IEEE Registration Authority detected" log spam
- MAC address now only shown in device info (not used for connections)

## [2025.10.16.2] - 2025-10-16

### Added
- Device IP address now shown as clickable link in device info card

## [2025.10.16.1] - 2025-10-16

### Added
- Options Flow for updating connection details after initial setup
- Support for multiple NetCommander devices via unique_id
- Ability to update IP address and credentials without removing integration

## [2025.10.16] - 2025-10-16

### Fixed
- Improved timeout error handling with proper asyncio.TimeoutError catching
- Better error messages for connection timeouts

## [2025.10.15.3] - 2025-10-15

### Fixed
- Removed stale bytecode (.pyc files) from release zip
- Integration loading issue resolved

## [2025.10.15.2] - 2025-10-15

### Fixed
- sys.path manipulation moved before imports in config_flow.py
- Resolved "No module named 'netcommander_lib'" error

## [2025.10.15] - 2025-10-15

### Added
- Initial release
- Home Assistant custom component
- CLI tool with Rich formatting
- Async Python API client library
- Switch entities for outlet control
- Sensor entities for current and temperature monitoring
- Button entities for outlet reboots
- Device info display (model, firmware, hardware version, MAC)
- Comprehensive test suite with pytest
- HACS compatibility

### Features
- 5-outlet support (NP-0501DU tested)
- Real-time status monitoring
- Configurable polling (default 30 seconds)
- UI-based configuration
- Multiple output formats for CLI (table, JSON, YAML)
- Environment variable support
- Type-safe Pydantic models
- Custom exception hierarchy

---

## Version History Summary

- **2025.10.16.4** - Dynamic outlet detection and configurable scan interval
- **2025.10.16.3** - Fixed device tracking spam
- **2025.10.16.2** - Added IP display in device info
- **2025.10.16.1** - Options Flow for credential updates
- **2025.10.16** - Improved timeout error handling
- **2025.10.15.3** - Fixed bytecode issue
- **2025.10.15.2** - Fixed import path issue
- **2025.10.15** - Initial release

---

## Upgrade Notes

### From 2025.10.15.x to 2025.10.16.4

**No action required** - upgrade is seamless:
- Existing 5-outlet configurations continue working
- Scan interval defaults to 30 seconds (existing behavior)
- Use Options Flow (Configure button) to adjust scan interval if desired
- If you have non-5-outlet devices, they'll now be detected automatically

### Breaking Changes

None - all changes are backward compatible.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting changes.

Report bugs and request features at: https://github.com/rmrfslashbin/netcommander/issues

---

**Made with ❤️ for the Home Assistant community**
