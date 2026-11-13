# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Maintenance
- Remove replaced legacy command/polling implementations and obsolete state tracking from the shared base class; require concrete feedback methods through an abstract interface.
- Remove unused Supervisor API permissions, config/SSL mounts and the disabled, unused HTTP port from the add-on manifest.
- Install PyYAML only from `requirements.txt`, without a second Alpine Python-YAML package.
- Update and pin GitHub Actions, enable Dependabot for Actions, generalize branch filters, and validate container builds for all five declared architectures.
- Check local documentation links and heading anchors in CI; consolidate experimental history here while retaining the old document URL and headings.
- Correct historical RSSI/smoke-payload descriptions, add the missing v1.2.3 notes, and clarify the v1.2.4 publication date.
- Include the complete Apache-2.0 license and preserve the original copyright notice.

### Deliberately unchanged
- Google site verification, release tags, add-on version 1.3.0, MQTT topics/IDs, Python dependencies and all five declared architectures.
- Alpine 3.18/Python 3.11 base-image migration is a separate follow-up, not part of this cleanup.
- No new release is published by this maintenance change.

## [1.3.0] - 2026-11-13

### Added
- Promote the tested feedback implementation to the production entry point, with stable add-on name, slug, MQTT client ID, topics, and discovery IDs.
- Publish accepted-command cover movement separately from real polled positions.
- Track pending commands per device with replacement, target reconciliation, and an independent configurable watchdog (`command_feedback_timeout`, default 120 seconds).
- Add production packaging, configuration serialization, dependency, and version-contract tests plus Python and amd64 container CI.

### Changed
- Default polling to 30 seconds; serialize MiniSafe HTTP access and space GetStates starts, including startup. No command-triggered polling or automatic retries.
- Enable optimistic Home Assistant switches/dimmers with real state feedback; keep covers non-optimistic and preserve raw position semantics.
- Upgrade `paho-mqtt` from 2.1.0 to 2.2.0 ([PR #25](https://github.com/Olgrov/eltako2mqtt/pull/25)); retain VERSION2 callbacks.
- Install Docker Python dependencies exclusively from `requirements.txt`; retain aiohttp 3.14.5 and PyYAML 6.0.3.
- Update every current documentation guide, release notes, migration instructions, topic contracts, and test plan.

### Fixed
- Package the actual production feedback module instead of referencing a missing `state_feedback.py`.
- Forward the optional feedback timeout through the add-on launcher and safely serialize credentials without shell interpolation.
- Preserve the latest accepted cover direction across delayed/opposite feedback; never fabricate target positions.
- Ignore invalid dimmer brightness instead of publishing a fabricated zero; preserve valid state and RSSI.
- Avoid logging request URLs from command exceptions because they can contain MiniSafe credentials.
- Publish each actuator discovery config once with its final feedback settings, rather than briefly sending legacy settings first.

### Upgrade notes
- Existing production configuration remains usable; omitted feedback timeout defaults to 120 seconds. Existing polling intervals are not silently changed; 30 seconds or more is recommended.
- Stop any experimental add-on before starting production. Shared command topics/discovery IDs must not have two active bridge instances.
- Movement labels and timeout expiry are not independent motor-state confirmation. Power measurement is not included in 1.3.0.

## [1.2.5-test.3] - 2026-10-30

Experimental test branch only; not a production release.

### Fixed
- Preserve the latest accepted cover direction across stale or opposite-direction position feedback without changing polled positions.
- Bound assumed motion with an independent configurable feedback timeout (default 120 seconds), including when polling fails; no command retries or extra polls.
- Distinguish a position sample after an accepted stop from independently verified motor stop.
- Ignore missing/invalid dimmer brightness instead of publishing a fabricated zero; retain on/off and RSSI feedback, with per-device warning suppression until recovery.
- Track recently commanded devices independently, validate GetStates payloads, and cancel superseded/completed timeout tasks.

### Changed
- Update experimental add-on version, configuration, testing guide, and regression tests. Production bridge unchanged.
- Supersede the short stationary-snapshot grace behavior described for test.2 below.

## [1.2.5-test.2] - 2026-10-28

Experimental test branch only; superseded by test.3 and then production v1.3.0.

- Fix inverted movement and pending targets for cover slider commands. Home Assistant sends 0=closed / 100=open; the MiniSafe command/status coordinate is inverted.
- Stop holding polled movement labels until the diagnostic pending timeout (90 seconds with a 30-second interval). Positions remain published on every successful poll.
- Disable optimistic endpoint prediction for covers only. Command-accepted movement is still published immediately; switches and dimmers remain optimistic.
- Accept numeric strings in raw cover positions; reject missing, non-finite, and out-of-range positions without inventing endpoints.
- Derive polled movement from position changes; an unchanged snapshot stops the assumed motion after a short two-second grace period. This is an estimate, not a motor-running sensor.
- Space GetStates start times by at least the configured interval, including startup; serialize requests without holding the lock while waiting for the next poll.
- Add DEBUG logs for request timing, raw position, expected target, movement, and pending age.
- Add 19 automated regression tests with mocked HTTP/MQTT. Physical hardware, frontend behavior, and container builds still require practical verification.

## [1.2.5-test.1] - 2026-10-27

Experimental test branch only; not a production release.

- Initial isolated optimistic-feedback experiment with cover movement topics, diagnostic pending commands, serialized MiniSafe requests, and 30-second default polling.

## [1.2.5] - 2026-10-27

### Changed
- Updated `aiohttp` from 3.14.3 to 3.14.5 in `requirements.txt` and `Dockerfile`.
- Updated the Home Assistant add-on version and Docker image label from 1.2.4 to 1.2.5.
- Updated README, installation guide, and release documentation for v1.2.5.

### Compatibility
- No changes to device handling, MQTT topics, Home Assistant discovery, or add-on configuration.
- Fully backward compatible with v1.2.4 and earlier v1.2.x releases.

<a name="124---2026-08-02"></a>

## [1.2.4] - 2026-09-03

### Changed
- Updated aiohttp dependency from 3.14.2 to 3.14.3 in requirements.txt.
- Date follows the GitHub release publication; the dependency PR was merged on 2026-07-31.

## [1.2.3] - 2026-07-25

### Changed
- Updated aiohttp dependency from 3.14.1 to 3.14.2 in requirements.txt and Dockerfile.

## [1.2.2] - 2026-06-15

### Changed
- Updated aiohttp dependency from 3.13.5 to 3.14.1 in requirements.txt and Dockerfile.

## [1.2.1] - 2026-04-02

### Changed
- Updated aiohttp dependency to 3.13.5 in the Docker image to match requirements.txt.

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
  - RSSI MQTT topic for signal strength in percent; no dedicated discovery sensor
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
- Device discovery published at bridge startup and when Home Assistant reports online

## [1.1.0] - 2026-01-09

### Added
- **Defensive Brightness Handling** - Improved `eltako_level_to_mqtt_brightness()` with robust error handling
  - Handles None, string inputs, and over-limit values gracefully
  - Validates input before conversion (0-100 range)
  - Informative logging for invalid brightness values
  - Graceful fallback to 0 for invalid inputs
