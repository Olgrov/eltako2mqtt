# Experimental changelog

This is the historical record of `test/optimistic-state-feedback`, not a separate production installation guide.
The tested implementation was promoted to production in v1.3.0; use [the production test plan](TESTING_OPTIMISTIC_STATE.md) and [release notes](RELEASE_NOTES.md) for current behavior.

## Promotion to 1.3.0 - 2026-11-13

- Rename the feedback module/class to production names and use it through the standard `eltako2mqtt.py` entry point.
- Restore production identity and remove the experimental launcher; retain MQTT topics and discovery IDs.
- Forward the optional feedback timeout and document migration without running both add-ons simultaneously.

## 1.2.5-test.3 - 2026-10-30

- Preserve the latest accepted direction across old/opposite feedback until target, replacement, or independent configurable timeout.
- Keep polled positions unchanged, reject invalid brightness, validate GetStates payloads, and cancel superseded/completed watchdogs.
- Distinguish accepted Stop plus a position sample from independent motor-stop confirmation.
- Supersede the short stationary-snapshot grace behavior described for test.2 below.

## 1.2.5-test.2 — 2026-10-28

- Fix inverted movement and pending targets for cover slider commands. Home Assistant sends 0=closed / 100=open; the MiniSafe command/status coordinate is inverted.
- Stop holding polled movement labels until the diagnostic pending timeout (90 seconds with a 30-second interval). Positions remain published on every successful poll.
- Disable optimistic endpoint prediction for covers only. Command-accepted movement is still published immediately; switches and dimmers remain optimistic.
- Accept numeric strings in raw cover positions; reject missing, non-finite, and out-of-range positions without inventing endpoints.
- Derive polled movement from position changes; an unchanged snapshot stops the assumed motion after a short two-second grace period. This is an estimate, not a motor-running sensor.
- Space GetStates start times by at least the configured interval, including startup; serialize requests without holding the lock while waiting for the next poll.
- Add DEBUG logs for request timing, raw position, expected target, movement, and pending age.
- Add 19 automated regression tests with mocked HTTP/MQTT. Physical hardware, frontend behavior, and container builds still require practical verification.

## 1.2.5-test.1 — 2026-10-27

- Initial isolated optimistic-feedback experiment with cover movement topics, diagnostic pending commands, serialized MiniSafe requests, and 30-second default polling.
