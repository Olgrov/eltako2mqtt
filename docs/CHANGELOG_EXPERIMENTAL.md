# Experimental changelog

These builds exist only on `test/optimistic-state-feedback`; they are not production releases.

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
