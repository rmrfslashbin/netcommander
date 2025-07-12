# Physical Outlet Mapping Test

Based on your testing, let me document what we know:

## Current Status
Status string: `01000` = outlets 1,3,4,5 OFF, outlet 2 ON

## Test Results So Far
1. **Clicking HA "Outlet 1 OFF"**: 
   - Status changed from `11110` to `01110` 
   - Physical result: Outlet 1 turned OFF ✓ (CORRECT)

2. **Clicking HA "Outlet 3 OFF"**:
   - Status changed from `01110` to `01010`
   - Physical result: Need to verify which physical outlet changed

3. **Clicking HA "Outlet 4 OFF"**:
   - Status changed from `01010` to `01000`  
   - Physical result: You said #2 turned OFF (not #4!)

## Hypothesis
The device may have this mapping:
- Status position 0 = Physical outlet 1 ✓
- Status position 1 = Physical outlet ?
- Status position 2 = Physical outlet ?  
- Status position 3 = Physical outlet 2 (based on your observation)
- Status position 4 = Physical outlet ?

## Next Test
Can you:
1. Turn everything ON first (get to `11111`)
2. Click HA "Outlet 2 OFF" and tell me which physical outlet turns off
3. Click HA "Outlet 5 OFF" and tell me which physical outlet turns off

This will help us map all positions correctly.