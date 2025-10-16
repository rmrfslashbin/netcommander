# Factory Reset Guide for NP-0501DU

**Device**: Synaccess netBooter NP-0501DU
**Date**: 2025-10-15
**Reason**: Device in broken state with inverted logic, commands failing

---

## Problem Summary

### Current Issues
1. **All outlets report inverted state** - Status says OFF when outlets have power
2. **LEDs don't match reality** - LEDs OFF when outlets are powered
3. **Explicit commands fail** - `$A3` and `$A7` commands return `$AF` (failed)
4. **Only toggle works** - `rly=X` command works but doesn't fix the state
5. **Web interface locks unchecked** - Not a permissions issue
6. **No configuration options** - No settings for relay logic or power states

### Attempted Fixes
- ✗ Reboot device - No change
- ✗ Explicit ON/OFF commands (`$A3`) - Returns `$AF` (failed)
- ✗ Set all commands (`$A7`) - Returns `$AF` (failed)
- ✗ Web interface unlock - Already unlocked
- ✗ Configuration settings - None available

**Conclusion**: Factory reset is the only remaining option.

---

## Factory Reset Procedure

From the manual (Part #1291 V4, Page 2):

> "To restore the factory default settings, you need to press a push-button switch located on the front panel for **20 seconds**."

### Steps

1. **Locate the Reset Button**
   - Look on the **front panel** of the device
   - Button may be labeled "Rst", "Default", or "Reset"
   - Likely recessed (may need a paperclip or pen)

2. **Press and Hold**
   - Press the button with a paperclip/pen
   - **Hold for 20 seconds**
   - You may see LEDs flash or change during this time

3. **Release and Wait**
   - Release the button after 20 seconds
   - Wait for device to reboot (30-60 seconds)
   - All LEDs should go through a boot sequence

4. **Verify Reset**
   - Device will return to default IP: **192.168.1.100**
   - Your computer must be on 192.168.1.x subnet to access it
   - Default credentials: **admin / admin**

---

## Post-Reset Configuration

### Network Setup (If needed)

If you need to keep using 192.168.50.x network:

**Option A: Use temporary static IP on your computer**
1. Set your computer to static IP: 192.168.1.50
2. Access device at http://192.168.1.100
3. Login: admin/admin
4. Change device IP back to 192.168.50.224
5. Restore your computer's network settings

**Option B: Use DHCP on device**
1. Before reset, configure your DHCP server to assign 192.168.50.224 to the device's MAC
2. After reset:
   - Shutdown device
   - Press reset button while powering on
   - Hold for 3 seconds after power on
   - Device will boot with DHCP enabled

### Security Setup
1. **Change default password** immediately
2. Update admin password to your current one
3. Configure network settings (IP, subnet, gateway)

### Outlet Verification

After reset, **immediately test** outlet behavior:

1. **Check initial state** (all outlets should be OFF after reset)
   ```bash
   curl -u admin:admin "http://192.168.1.100/cmd.cgi?\$A5"
   # Expected: $A0,00000,0.00,XX
   ```

2. **Turn on ONE outlet** via web interface
   - Click outlet 1 to turn ON
   - **Verify LED turns ON** ✓
   - **Verify outlet has POWER** ✓ (test with multimeter/load)

3. **Check status matches reality**
   ```bash
   curl -u admin:admin "http://192.168.1.100/cmd.cgi?\$A5"
   # Expected: $A0,00001,0.XX,XX (bit 4 = 1 for outlet 1)
   ```

4. **If still inverted → HARDWARE FAULT**
   - This would indicate a hardware or firmware defect
   - Contact Synaccess support
   - Consider RMA (return for replacement)

---

## Expected Results After Reset

### ✅ If Reset Fixes the Problem

```
Status Report: $A0,00001,0.15,XX
Outlet 1: LED=ON, Power=ON, Status bit=1  ← All aligned!
```

- LEDs will match outlet power state
- Status bits will match reality
- Explicit commands (`$A3`) will work (no `$AF` errors)

### ❌ If Problem Persists

```
Status Report: $A0,00000,0.15,XX
Outlet 1: LED=OFF, Power=ON, Status bit=0  ← Still inverted!
```

This indicates:
- **Hardware defect** - Relay wiring issue
- **Firmware bug** - Deep firmware corruption
- **Factory defect** - Unit may have left factory in bad state

**Action Required**: Contact Synaccess support at:
- Website: www.synaccess-net.com/support
- Phone: (928) 257-xxxx (from manual)
- Email: support@synaccess-net.com (likely)

Provide them with:
- Model: NP-0501DU
- Serial number (on device label)
- This test data showing inverted logic
- `outlet_mapping_results_20251015_131625.json`

---

## Backup Current Configuration (Optional)

Before reset, you may want to save current settings:

### Via Manual Download
1. Login to web interface
2. Look for "Save Settings" or "Backup" option
3. Download configuration file

### Via syncfg.exe Tool (Windows only)
From manual:
> Download "synCfg.exe" by visiting www.synaccess-net.com/support
> Run the program at DOS prompt: "syncfg.exe –h"

**Note**: Since device is in broken state, saved config may restore the broken state too!

---

## Alternative: Firmware Update

Before or after reset, check for firmware updates:

1. Login to web interface
2. Look for "System Info" or "About" page
3. Note current firmware version
4. Visit www.synaccess-net.com/support
5. Check for newer firmware for NP-0501DU
6. Follow their upgrade instructions

**Warning**: Firmware upgrade can brick device if interrupted. Ensure stable power!

---

## Test Script for Post-Reset Verification

After reset, run this to verify device is working correctly:

```bash
# Test script
source .venv/bin/activate
python test_device_discovery.py

# Should show:
# - Status matches reality
# - LEDs match power state
# - No inverted logic
```

---

## Checklist

Before reset:
- [ ] Backup any important settings (if possible)
- [ ] Note current IP configuration
- [ ] Have paperclip/pen ready for button
- [ ] Plan network access strategy (temp static IP or DHCP)

After reset:
- [ ] Verify device boots (LEDs active)
- [ ] Access at 192.168.1.100
- [ ] Login with admin/admin
- [ ] Test ONE outlet thoroughly
- [ ] Verify status matches reality
- [ ] If fixed: reconfigure network settings
- [ ] If broken: contact Synaccess support

---

## Decision Point

**If factory reset doesn't fix the inverted logic:**

This device is fundamentally broken and should **NOT** be used in production:
- Safety hazard (can't trust status)
- Unreliable automation
- Potential equipment damage

**Options:**
1. **Return/RMA** - Get replacement unit
2. **Use as-is** - Build software workaround (not recommended for production)
3. **Replace** - Buy different PDU model

**My recommendation**: If reset doesn't fix it, pursue RMA/replacement. Don't build automation around a broken device.

---

**Last Updated**: 2025-10-15
**Status**: Ready for factory reset attempt
