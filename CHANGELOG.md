# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2026-02-05

### Added
- **FSR14 Switch Actuator Support** - Full support for FSR14 switch family
  - FSR14 (1-4 channels)
  - FSR14M-2x (with power measurement)*
  - FSR14SSR (Solid State Relay)
  - F4SR14-LED (4-channel for LED control)
  - FAE14LPR, FAE14SSR (switch actuators)
- **FRWB Smoke Detector Support** - Complete integration for smoke detectors
  - Binary sensor for smoke alarm detection
  - Temperature sensor (built-in FRWB sensor)
  - RSSI sensor for signal strength monitoring
- **`is_switch_device()` Helper Function** - Centralized switch device detection
  - Cleaner, more maintainable code structure
  - Easy extension for future switch variants
  - Single source of truth for device type checking

*Power measurement sensors can be added in future releases

### Changed
- Refactored switch device detection logic into reusable helper function
- Updated `build_command_url()` to use new helper for switch detection
- Updated `update_device_state_immediate()` to use new helper
- Updated `publish_device_state()` to use new helper
- Updated `publish_discovery()` to use new helper
- Updated `_log_device_feedback()` to use new helper

### Technical Details
- Multi-channel devices (FSR14-4x, etc.) automatically supported via MiniSafe2's consecutive SID assignment
- Each channel appears as separate switch entity in Home Assistant
- Smoke detectors use proven multi-sensor pattern (similar to weather stations)
- All new device types leverage existing MQTT discovery infrastructure
- Switch commands: `on`, `off`, `toggle` (standard binary control)

### Compatibility
- Fully backward compatible - no breaking changes
- Existing configurations work without modification
- New devices auto-discovered on next poll cycle

## [1.1.0] - 2026-01-09

### Added
- **Defensive Brightness Handling** - Improved `eltako_level_to_mqtt_brightness()` with robust error handling
  - Handles None, string inputs, and over-limit values gracefully
  - Validates input before conversion (0-100 range)
  - Informative logging for invalid brightness values
  - Graceful fallback to 0 for invalid inputs
- **Position-Based Blind Commands** - New position control for blinds (0-100)
  - Automatic position inversion for Eltako device compatibility
  - Commands: `moveTo0` (open) to `moveTo100` (closed)
  - Prevents immediate state update for blinds (waits for hardware feedback)
- **Enhanced Hardware Feedback Logging** - Connection-aware logging
  - Only logs when MQTT broker is connected
  - Smart device-specific logging (only recently commanded device shows feedback)
  - Reduces log noise and improves debugging clarity
- **Dynamic Command Timeout** - Configurable timeout based on poll interval
  - Calculation: `poll_interval + 60 seconds`
  - Example: 5s poll → 65s timeout window
  - Better visibility into device state changes during debugging with DEBUG logging level
- **Logging Level Configuration** - Configurable via `config.yaml`
  - Set logging level (DEBUG, INFO, WARNING, ERROR)
  - Better control over verbosity

### Changed
- **Default poll_interval reduced from 15 to 5 seconds** for more responsive updates
- Improved logging clarity with connection-aware feedback messages
- Command timeout is now configurable through poll_interval setting
- Optimized polling behavior for faster device state synchronization
- Blind commands now use lowercase payloads: `open`, `close`, `stop` (was UPPERCASE)
- Better YAML generation in `run.sh` for mqtt credentials

### Fixed
- Excessive logging output when DEBUG level enabled (now filtered by MQTT connection status)
- All devices being logged on every poll cycle (now only commanded device shows feedback)
- Hardware feedback appearing regardless of connection state
- Dimmer crash risk from invalid brightness values (now defensive validation)
- Blind position inversion causing confusion in Home Assistant UI
- MQTT credential handling in run.sh (improved sed-based YAML generation)

### Technical Details
- Added `mqtt_connected` flag to track broker connection state
- Added `_recently_commanded_device` tracking for targeted logging
- Added `_is_recently_commanded()` method for timeout window checking
- Added `_log_device_feedback()` method for smart logging
- Timeout calculation: `poll_interval + 60 seconds`
- MQTT connection status is checked before logging any hardware feedback
- Blind device state is NOT immediately updated (waits for hardware feedback via polling)

### Compatibility
- Fully backward compatible - no breaking changes for users
- Existing config.yaml files work without changes
- Blind commands in Home Assistant will now correctly reflect inverted position

## [1.0.5] - Previous Release

For previous releases, see git history.
