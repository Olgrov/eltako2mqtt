# Changelog

All notable changes to this project will be documented in this file.

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
