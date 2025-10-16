# Home Assistant Automation Examples

This guide provides example automations for the Synaccess NetCommander integration.

## Table of Contents

1. [Power Management](#power-management)
2. [Scheduled Operations](#scheduled-operations)
3. [High Current Alerts](#high-current-alerts)
4. [Temperature Monitoring](#temperature-monitoring)
5. [Device Rebooting](#device-rebooting)
6. [Smart Home Integration](#smart-home-integration)

---

## Power Management

### Turn Off All Outlets at Night

Automatically power down all outlets at a specific time to save energy:

```yaml
automation:
  - alias: "NetCommander - Power Down at Night"
    description: "Turn off all outlets at 11 PM"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: switch.turn_off
        target:
          entity_id:
            - switch.netcommander_outlet_1
            - switch.netcommander_outlet_2
            - switch.netcommander_outlet_3
            - switch.netcommander_outlet_4
            - switch.netcommander_outlet_5
```

### Turn On Outlets When Home

Power up devices when you arrive home:

```yaml
automation:
  - alias: "NetCommander - Power On When Home"
    description: "Turn on outlets when arriving home"
    trigger:
      - platform: state
        entity_id: person.your_name
        to: "home"
    action:
      - service: switch.turn_on
        target:
          entity_id:
            - switch.netcommander_outlet_1
            - switch.netcommander_outlet_2
```

---

## Scheduled Operations

### Nightly Server Reboot

Reboot a server connected to outlet 1 every night at 3 AM:

```yaml
automation:
  - alias: "NetCommander - Nightly Server Reboot"
    description: "Reboot server at 3 AM daily"
    trigger:
      - platform: time
        at: "03:00:00"
    action:
      - service: button.press
        target:
          entity_id: button.netcommander_reboot_outlet_1
```

### Weekday/Weekend Schedules

Different power schedules for weekdays and weekends:

```yaml
automation:
  - alias: "NetCommander - Weekday Morning Power On"
    description: "Turn on work equipment on weekdays"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.netcommander_outlet_3

  - alias: "NetCommander - Weekend Late Power On"
    description: "Turn on equipment later on weekends"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: time
        weekday:
          - sat
          - sun
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.netcommander_outlet_3
```

---

## High Current Alerts

### Current Threshold Alert

Get notified when total current exceeds a threshold:

```yaml
automation:
  - alias: "NetCommander - High Current Alert"
    description: "Alert when current exceeds 4.0 Amps"
    trigger:
      - platform: numeric_state
        entity_id: sensor.netcommander_total_current
        above: 4.0
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ NetCommander High Current"
          message: "Current draw is {{ states('sensor.netcommander_total_current') }} Amps"
          data:
            priority: high
```

### Load Shedding

Automatically turn off non-critical outlets when current is too high:

```yaml
automation:
  - alias: "NetCommander - Load Shedding"
    description: "Turn off outlet 5 when current exceeds 4.5A"
    trigger:
      - platform: numeric_state
        entity_id: sensor.netcommander_total_current
        above: 4.5
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.netcommander_outlet_5
      - service: notify.mobile_app
        data:
          title: "🔌 Load Shedding Activated"
          message: "Outlet 5 turned off due to high current"
```

---

## Temperature Monitoring

### Temperature Alert

Monitor device temperature and alert if it gets too hot:

```yaml
automation:
  - alias: "NetCommander - High Temperature Alert"
    description: "Alert when device temperature exceeds 60°C"
    trigger:
      - platform: numeric_state
        entity_id: sensor.netcommander_temperature
        above: 60
    action:
      - service: notify.mobile_app
        data:
          title: "🌡️ NetCommander Overheating"
          message: "Device temperature is {{ states('sensor.netcommander_temperature') }}°C"
          data:
            priority: high
```

---

## Device Rebooting

### Auto-Reboot on Ping Failure

Reboot a device if it stops responding to pings:

```yaml
automation:
  - alias: "NetCommander - Auto Reboot on Ping Failure"
    description: "Reboot outlet 1 if server stops responding"
    trigger:
      - platform: state
        entity_id: binary_sensor.server_ping
        to: "off"
        for:
          minutes: 5
    action:
      - service: notify.mobile_app
        data:
          title: "🔄 Server Not Responding"
          message: "Rebooting server on outlet 1"
      - service: button.press
        target:
          entity_id: button.netcommander_reboot_outlet_1
      - delay:
          seconds: 60
      - service: notify.mobile_app
        data:
          title: "✅ Server Reboot Complete"
          message: "Outlet 1 has been power cycled"
```

### Scheduled Weekly Reboot

Reboot networking equipment weekly:

```yaml
automation:
  - alias: "NetCommander - Weekly Network Reboot"
    description: "Reboot router/modem every Sunday at 4 AM"
    trigger:
      - platform: time
        at: "04:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: button.press
        target:
          entity_id:
            - button.netcommander_reboot_outlet_2
            - button.netcommander_reboot_outlet_3
```

---

## Smart Home Integration

### Sync with Room Lights

Turn outlets on/off when specific lights are controlled:

```yaml
automation:
  - alias: "NetCommander - Sync with Office Lights"
    description: "Turn on outlet when office lights turn on"
    trigger:
      - platform: state
        entity_id: light.office
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.netcommander_outlet_4

  - alias: "NetCommander - Sync Off with Office Lights"
    description: "Turn off outlet when office lights turn off"
    trigger:
      - platform: state
        entity_id: light.office
        to: "off"
        for:
          minutes: 5
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.netcommander_outlet_4
```

### Power Consumption Dashboard

Create a sensor template for power calculations:

```yaml
template:
  - sensor:
      - name: "NetCommander Estimated Power"
        unit_of_measurement: "W"
        state: "{{ (states('sensor.netcommander_total_current') | float * 120) | round(1) }}"
        device_class: power
```

### Outlet Status Summary

Create a sensor that summarizes outlet states:

```yaml
template:
  - sensor:
      - name: "NetCommander Status Summary"
        state: >
          {% set total = 5 %}  {# Adjust for your device #}
          {% set on = states('sensor.netcommander_outlets_on') | int %}
          {% set off = total - on %}
          {{ on }} on, {{ off }} off
        icon: mdi:power-socket-us
```

---

## Advanced: Multi-Outlet Patterns

### Sequential Power On

Turn on outlets one at a time with delays (reduces inrush current):

```yaml
automation:
  - alias: "NetCommander - Sequential Power On"
    description: "Turn on all outlets with delays"
    trigger:
      - platform: state
        entity_id: input_boolean.power_on_sequence
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.netcommander_outlet_1
      - delay:
          seconds: 5
      - service: switch.turn_on
        target:
          entity_id: switch.netcommander_outlet_2
      - delay:
          seconds: 5
      - service: switch.turn_on
        target:
          entity_id: switch.netcommander_outlet_3
      - delay:
          seconds: 5
      - service: switch.turn_on
        target:
          entity_id: switch.netcommander_outlet_4
      - delay:
          seconds: 5
      - service: switch.turn_on
        target:
          entity_id: switch.netcommander_outlet_5
```

### Vacation Mode

Turn outlets on/off randomly to simulate presence:

```yaml
automation:
  - alias: "NetCommander - Vacation Mode"
    description: "Random outlet control when away"
    trigger:
      - platform: time_pattern
        hours: "/2"  # Every 2 hours
    condition:
      - condition: state
        entity_id: input_boolean.vacation_mode
        state: "on"
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ range(0, 2) | random == 0 }}"
            sequence:
              - service: switch.toggle
                target:
                  entity_id: switch.netcommander_outlet_1
          - conditions:
              - condition: template
                value_template: "{{ range(0, 2) | random == 0 }}"
            sequence:
              - service: switch.toggle
                target:
                  entity_id: switch.netcommander_outlet_2
```

---

## Tips for Creating Automations

1. **Test First**: Use Developer Tools → Services to test commands before creating automations
2. **Use Delays**: Add delays between power operations to avoid electrical surges
3. **Add Notifications**: Include mobile notifications for important state changes
4. **Label Outlets**: Name your outlets in Home Assistant for easier automation creation
5. **Check Current**: Monitor `sensor.netcommander_total_current` to avoid overload
6. **Adjust Entity IDs**: Replace entity IDs with your actual device's entity IDs
7. **Dynamic Outlets**: If your device has 8 outlets, adjust entity IDs accordingly (outlet_1 through outlet_8)

---

## Debugging Automations

If your automation isn't working:

1. Check automation trace in Developer Tools → Automations
2. Verify entity IDs match your device
3. Check conditions are being met
4. Test the service calls manually first
5. Check Home Assistant logs for errors

---

## More Examples

For more automation ideas, see:
- [Home Assistant Automation Documentation](https://www.home-assistant.io/docs/automation/)
- [Home Assistant Community Forum](https://community.home-assistant.io/)
- [GitHub Issues](https://github.com/rmrfslashbin/netcommander/issues) - Share your automations!

---

**Made with ❤️ for the Home Assistant community**
