# Optimistic State Feedback Test Guide

This test branch separates immediate Home Assistant feedback from authoritative MiniSafe2 state polling.

## Behavior

- Home Assistant MQTT discovery uses optimistic mode for covers, switches, and lights.
- Successful cover commands publish `opening`, `closing`, or `stopped` immediately.
- Cached MiniSafe2 device state is never modified after a command.
- Actual state and position continue to come exclusively from `GetStates` during regular polling.
- MiniSafe2 HTTP operations are serialized to prevent overlapping `SendSC` and `GetStates` requests.
- A polling interval of at least 30 seconds is recommended; lower values produce a warning.

## Test Cases

1. Set `poll_interval` to 30 seconds and restart the experimental bridge.
2. Dim a light several times. The Home Assistant slider should react immediately and settle on the polled value without retained synthetic state.
3. Turn a switch on and off. The UI should react immediately; the next poll confirms or corrects it.
4. Open and close a blind. Home Assistant should immediately show opening or closing while the position remains hardware-derived.
5. Stop a moving blind. Home Assistant should immediately show stopped; the next poll updates its position.
6. Control a device outside Home Assistant. The next regular poll must update Home Assistant correctly.
7. Send commands close to a scheduled poll and verify logs contain no overlapping MiniSafe2 HTTP errors.
8. Set `poll_interval` below 30 seconds and verify that a stability warning is logged.

## Activation

For an add-on build of this branch, copy `eltako2mqtt_experimental.py` and `run-experimental.sh` into the image and use `/run-experimental.sh` as the container command. The production `eltako2mqtt.py` and `run.sh` remain unchanged intentionally.

## Useful Logs

With `logging.level: DEBUG`, look for:

- `Command successful for ...`
- `Command confirmed by MiniSafe2 for ...`
- `Command not confirmed for ...`
- The warning for polling intervals below 30 seconds
