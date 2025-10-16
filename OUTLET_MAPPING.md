# NP-0501DU Outlet Mapping - CRITICAL FINDINGS

**Device**: Synaccess netBooter NP-0501DU
**Firmware**: Unknown
**Test Date**: 2025-10-08
**Tested By**: Robert Sigler

## 🚨 INVERTED LOGIC DISCOVERED

**CRITICAL**: Outlets 1 and 5 have **INVERTED status reporting**. The device reports the OPPOSITE of the actual physical state.

## Verified Mappings

### Control Commands (rly=X)

| rly Index | Physical Outlet | Status Position | Logic Type |
|-----------|----------------|-----------------|------------|
| `rly=0`   | **Outlet 1**   | Position 4 (rightmost) | **INVERTED** |
| `rly=1`   | Outlet 2       | Position 3     | Unknown |
| `rly=2`   | Outlet 3       | Position 2     | Unknown |
| `rly=3`   | Outlet 4       | Position 1     | Unknown |
| `rly=4`   | **Outlet 5**   | Position 0 (leftmost) | **INVERTED** |

### Status String Mapping

Status format: `$A0,XXXXX,current,temp`

The 5-character outlet string maps as follows:

```
Position: 0     1     2     3     4
Outlet:   5     4     3     2     1
Index:   [0]   [1]   [2]   [3]   [4]
```

**Documentation confirmation**: "The most right x for relay1" ✓ CORRECT
- Rightmost bit (position 4) = Physical outlet 1
- Leftmost bit (position 0) = Physical outlet 5

## Inverted Logic Details

### Physical Outlet 1
- **Control**: `rly=0`
- **Status**: Position 4 (rightmost)
- **Problem**: When outlet 1 is physically ON:
  - Device reports: `0` (OFF)
  - Sending `rly=0` changes status to `1` (ON)
  - But physical outlet turns OFF
- **Effect**: Status bit is inverted from physical reality

### Physical Outlet 5
- **Control**: `rly=4`
- **Status**: Position 0 (leftmost)
- **Problem**: When outlet 5 is physically ON:
  - Device reports: `0` (OFF)
  - Sending `rly=4` changes status to `1` (ON)
  - But physical outlet turns OFF
- **Effect**: Status bit is inverted from physical reality

## Test Results

### Initial State
```
Physical Reality:  Outlet 1=ON, Outlet 5=ON, Others=OFF
Device Reports:    $A0,00000,0.15,XX (all OFF)
Current Draw:      0.15A (confirms power is being drawn)
```

### Test: rly=0 (Physical Outlet 1)
```
Before:  00000  (Device says: all OFF)
Command: rly=0
After:   00001  (Device says: outlet 1 is now ON)
Reality: Physical outlet 1 turned OFF
Result:  ⚠️ INVERTED - Device reports opposite of reality
```

### Test: rly=4 (Physical Outlet 5)
```
Before:  00000  (Device says: all OFF)
Command: rly=4
After:   10000  (Device says: outlet 5 is now ON)
Reality: Physical outlet 5 turned OFF
Result:  ⚠️ INVERTED - Device reports opposite of reality
```

## Outstanding Questions

1. **Are outlets 2, 3, 4 also inverted?** Need to test with loads connected
2. **Is this a firmware bug?** Device might have a known issue
3. **Is this configurable?** Web interface might have a setting for "Normally Open" vs "Normally Closed" relay logic
4. **Does this affect all NP-0501DU units?** Or just this one?

## Implications for Software Integration

### Home Assistant Integration
- **MUST** implement logic inversion for outlets 1 and 5
- Cannot trust device status directly
- Need configuration option to disable inversion (for other device models)

### CLI Tool
- Should detect inverted logic automatically
- Warn user if detected
- Provide `--invert-outlets` flag for affected outlets

### API Client Library
```python
class OutletConfig:
    outlet_number: int
    inverted_logic: bool = False  # Set True for outlets 1, 5 on NP-0501DU

def get_actual_state(reported_state: bool, inverted: bool) -> bool:
    """Get actual physical state accounting for inverted logic."""
    return not reported_state if inverted else reported_state
```

## Recommended Next Steps

1. ✅ **COMPLETED**: Test outlets 1 and 5
2. ⏳ **TODO**: Connect loads to outlets 2, 3, 4 and test for inverted logic
3. ⏳ **TODO**: Check device web interface for relay configuration settings
4. ⏳ **TODO**: Contact Synaccess support about firmware version and known issues
5. ⏳ **TODO**: Document whether this affects reboot commands (`rb=X`)
6. ⏳ **TODO**: Build software with configurable inversion per outlet

## Safety Warnings

⚠️ **DO NOT TRUST DEVICE STATUS FOR OUTLETS 1 AND 5**

- Device reports OFF when outlet is ON
- Device reports ON when outlet is OFF
- This could lead to:
  - Equipment damage (thinking power is off when it's on)
  - Safety hazards (attempting maintenance on "powered off" equipment)
  - Data loss (unexpected power cycles)

## Hardware Workaround

If possible:
- Use outlets 2, 3, 4 for critical loads
- Keep outlets 1 and 5 for non-critical devices
- Or implement software inversion (recommended)

---

**Last Updated**: 2025-10-08
**Status**: Partially tested - outlets 2, 3, 4 still need verification
