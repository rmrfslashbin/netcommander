---
name: Device Compatibility Report
about: Report compatibility with your Synaccess device
title: '[COMPAT] Device Model - Outlet Count'
labels: compatibility, documentation
assignees: ''
---

## Device Information

**Model**: <!-- e.g., NP-0801DU, NP-0501DU -->
**Outlet Count**: <!-- e.g., 5, 8 -->
**Firmware Version**:
**Hardware Version**:
**MAC Address**: <!-- Optional, last 4 digits only -->

<!-- Get device info using CLI: -->
```bash
python -m netcommander_cli.cli --host YOUR_IP --password YOUR_PASSWORD info
```

## Integration Status
- [ ] Successfully installed via HACS
- [ ] Device detected and configured
- [ ] All outlets show up in Home Assistant
- [ ] Correct number of entities created
- [ ] All switches work (on/off)
- [ ] All buttons work (reboot)
- [ ] Current sensor works
- [ ] Temperature sensor works

## Issues Encountered
<!-- Any problems during setup or use? Leave blank if everything works -->

## Additional Notes
<!-- Any other observations or comments -->

## Raw Device Response
<!-- Optional: Paste output from CLI info command -->
```
Paste here
```

---

**Thank you for testing!** Your report helps improve device compatibility for everyone.
