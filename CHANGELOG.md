# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-01-09

### Added
- Enhanced hardware feedback logging that only logs when MQTT broker is connected
- Smart device-specific logging: After sending a command to a device, only that device's hardware feedback is logged (not all devices)
- Dynamic command timeout calculation based on poll_interval + 60 seconds
- Better visibility into device state changes during debugging with DEBUG logging level

### Changed
- **Default poll_interval reduced from 15 to 5 seconds** for more responsive updates
- Improved logging clarity with connection-aware feedback messages
- Command timeout is now configurable through poll_interval setting
- Optimized polling behavior for faster device state synchronization

### Fixed
- Excessive logging output when DEBUG level enabled (now filtered by MQTT connection status)
- All devices being logged on every poll cycle (now only commanded device shows feedback)
- Hardware feedback appearing regardless of connection state

### Technical Details
- Added `mqtt_connected` flag to track broker connection state
- Added `_recently_commanded_device` tracking for targeted logging
- Timeout calculation: `poll_interval + 60 seconds` (e.g., 5s poll → 65s timeout)
- MQTT connection status is checked before logging any hardware feedback

## [1.0.5] - Previous Release

For previous releases, see git history.
