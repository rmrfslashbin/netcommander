# NetCommander Authentication Findings

## Summary

The previous AI implementation failed because it completely misunderstood the device's authentication mechanism. The device uses **standard HTTP Basic Authentication**, not the command-based authentication (`$A1`) that was attempted.

## Key Discoveries

### 1. Authentication Method
- **Working**: HTTP Basic Authentication (RFC 7617)
- **Not Required**: `$A1` login command (this is for telnet/serial interface)
- **Evidence**: Device returns `WWW-Authenticate: Basic realm="Protected"` header

### 2. API Status
- ✅ **Authentication**: Works perfectly with Basic Auth
- ✅ **Status Reading**: `$A5` command returns device status successfully
- ❌ **Outlet Control**: All control commands return `$AF` (failure)

### 3. Response Format
Status command (`$A5`) returns: `$A0,11111,0.07,XX`
- `$A0`: Success indicator
- `11111`: Outlet states (1=ON, 0=OFF) - 5 outlets in this device
- `0.07`: Current draw in amperes
- `XX`: Temperature or other data (device returns literal "XX")

### 4. Control Issue
All control commands fail with `$AF` response:
- `$A3,1,0` (turn outlet 1 off) → `$AF`
- `$A3,1,1` (turn outlet 1 on) → `$AF`
- `$A7,0` (all outlets off) → `$AF`
- `$A1` (login command) → `$AF`
- `$A2` (logout command) → `$AF`

## Possible Causes for Control Failure

1. **User Permissions**
   - The `admin` user might have read-only access
   - Device might have separate control credentials

2. **Device Configuration**
   - Outlets might be in "manual only" mode
   - Web control might be disabled in device settings
   - Device might require physical button press to enable control

3. **Missing Protocol Step**
   - Despite Basic Auth working, device might need additional initialization
   - Possible CSRF token or session cookie requirement
   - May need to access web UI first to establish full session

## Implementation Status

### New API (`netcommander_api.py`)
- ✅ Proper session management with persistent `ClientSession`
- ✅ HTTP Basic Authentication
- ✅ Status reading and parsing
- ✅ Clean error handling
- ⚠️  Control commands implemented but return failures

### Home Assistant Integration
- 🔄 Needs update to use new API
- 🔄 Should handle read-only mode gracefully
- 🔄 Consider making switches read-only if control not available

## Next Steps for User

1. **Check Device Configuration**
   - Access device web interface manually
   - Verify if outlets can be controlled via web
   - Check user permissions in device settings

2. **Try Different Credentials**
   - Device might have separate admin/control users
   - Check device manual for default control credentials

3. **Packet Capture** (if needed)
   - Use browser dev tools to capture successful manual control
   - Look for additional headers, cookies, or tokens

## Code Quality

The new implementation is significantly better:
- Proper async/await patterns
- Type hints and dataclasses
- Comprehensive error handling
- Session reuse for performance
- Clear separation of concerns

The previous implementation's core mistake was assuming the device used its command protocol for authentication, when it actually uses standard HTTP Basic Auth for the web interface.