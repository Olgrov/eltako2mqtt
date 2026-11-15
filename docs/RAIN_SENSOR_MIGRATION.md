# Rain sensor: moisture binary sensor

The weather station rain entity is now discovered as a Home Assistant
`binary_sensor` with `device_class: moisture`, rather than a text `sensor`.
The MQTT state topic `eltako/<SID>/rain` and its `true` / `false` payloads
remain unchanged. `true` maps to on (wet); `false` maps to off (dry).

## Existing installations

On discovery publication, the bridge clears the legacy retained configuration
at `homeassistant/sensor/eltako_weather_rain_<SID>/config` before publishing
the new configuration at
`homeassistant/binary_sensor/eltako_weather_rain_<SID>/config`.
This cleanup is repeated safely on startup and Home Assistant birth messages.
Only the old rain discovery configuration is cleared, not the state topic.

The entity domain changes from `sensor` to `binary_sensor`. After installing
a version containing this fix, check the actual new entity ID in Home Assistant
and update dashboards, templates and automations that referenced the old entity.
For Home Assistant state conditions use `on` / `off`, not the MQTT payload
strings `true` / `false`. Recheck entity-specific names, area overrides and other
customizations; history and entity registry settings are not migrated by this fix.

No release is created and no add-on version is bumped by this patch alone.
Dashboard summary inclusion depends on Home Assistant's own selection rules.
