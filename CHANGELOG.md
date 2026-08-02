# Changelog

All notable changes to this project will be documented in this file.

## [1.2.4] - 2026-08-02

### Changed
- Updated aiohttp dependency from 3.14.2 to 3.14.3 in requirements.txt.

## [1.2.3] - 2026-07-25

### Changed
- Updated aiohttp dependency from 3.14.1 to 3.14.2 in requirements.txt and Dockerfile.
- Bumped add-on version to 1.2.3 in config.yaml and Docker labels.

## [1.2.2] - 2026-06-15

### Changed
- Updated aiohttp dependency from 3.13.5 to 3.14.1 in requirements.txt and Dockerfile.
- Bumped add-on version to 1.2.2 in config.yaml and Docker labels.

## [1.2.1] - 2026-04-02

### Changed
- Updated aiohttp dependency to 3.13.5 in the Docker image to match requirements.txt.
- Bumped add-on version to 1.2.1 in config.yaml and Docker labels.

### Fixed
- Inconsistency between Dockerfile and requirements.txt aiohttp versions.
- Inconsistency between add-on version and Docker image label version.

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
