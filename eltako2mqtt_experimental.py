#!/usr/bin/env python3
"""Experimental optimistic Home Assistant feedback for Eltako2MQTT."""

import asyncio
import importlib.util
import json
import logging
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

spec = importlib.util.spec_from_file_location("eltako2mqtt_base", Path(__file__).with_name("eltako2mqtt.py"))
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
logger = logging.getLogger(__name__)


class ExperimentalBridge(base.EltakoMiniSafe2Bridge):
    def __init__(self, config_file: str):
        super().__init__(config_file)
        self.poll_interval = self.eltako_config.get("poll_interval", 30)
        self._command_timeout = self.poll_interval + 60
        logger.info("Experimental bridge 1.2.5-test.2; poll interval=%ss", self.poll_interval)
        self.pending_commands: Dict[str, Dict[str, Any]] = {}
        self._last_command_time: Dict[str, float] = {}
        self.minisafe_lock = asyncio.Lock()
        self._last_poll_started: Optional[float] = None
        self._cover_movements: Dict[str, str] = {}
        if self.poll_interval < 30:
            logger.warning("poll_interval below 30 seconds may destabilize MiniSafe2; 30+ is recommended")

    async def handle_device_command(self, sid: str, command: str):
        logger.info(f"Handling command for {sid}: '{command}'")
        if sid not in self.devices:
            logger.warning(f"Unknown device SID: {sid}")
            return
        device = self.devices[sid]
        url = self.build_command_url(device, command)
        if not url:
            logger.warning(f"Ignoring unsupported command: {command}")
            return
        try:
            async with self.minisafe_lock:
                async with self.session.get(url) as response:
                    text = await response.text()
                    if response.status == 200 and "{XC_SUC}" in text:
                        logger.info(f"Command successful for {sid}: {command}")
                        self._track_pending(sid, command, self.devices.get(sid, device))
                        await self._publish_command_feedback(sid)
                    else:
                        logger.error(f"Command failed for {sid} ({command}): {text}")
        except Exception as exc:
            logger.error(f"Error sending command to {sid}: {exc}")

    def _track_pending(self, sid: str, command: str, device: Dict[str, Any]):
        now = time.monotonic()
        cmd = command.strip().lower()
        device_type = device.get("data", "").lower()
        expected: Dict[str, Any] = {}
        movement: Optional[str] = None
        if "dimmer" in device_type:
            if cmd == "on":
                expected["state"] = "on"
            elif cmd == "off":
                expected = {"state": "off", "level": 0}
            elif self.is_numeric(command):
                value = float(command)
                level = round(value * 100 / 255) if 0 <= value <= 255 else None
                if level is not None:
                    expected = {"state": "on" if level else "off", "level": level}
        elif self.is_switch_device(device_type):
            if cmd in ("on", "off"):
                expected["state"] = cmd
            elif cmd == "toggle":
                current = device.get("state", {}).get("state", "off")
                expected["state"] = "off" if current == "on" else "on"
        elif "blind" in device_type:
            current = self._cover_position(device)
            if self.is_numeric(command):
                # The discovery template sends HA's percentage, not the inverted range.
                # Match build_command_url(): HA 0=closed -> MiniSafe moveTo100.
                target = 100 - int(float(command))
                expected["pos"] = target
                if current is not None:
                    movement = ("opening" if target < current else
                                "closing" if target > current else "stopped")
            elif cmd in ("open", "up"):
                expected["pos"], movement = 0, "opening"
            elif cmd in ("close", "down"):
                expected["pos"], movement = 100, "closing"
            elif cmd == "stop":
                movement = "stopped"
        self.pending_commands[sid] = {"command": command, "expected": expected, "movement": movement, "timestamp": now}
        self._recently_commanded_device = sid
        self._last_command_time[sid] = now
        logger.debug("Command tracking %s: command=%s raw_target=%s movement=%s",
                     sid, command, expected.get("pos"), movement)

    async def _publish_command_feedback(self, sid: str):
        movement = self.pending_commands[sid].get("movement")
        if movement:
            self.mqtt_client.publish(f"eltako/{sid}/movement", movement, retain=False)

    def _pending_matches(self, pending: Dict[str, Any], device: Dict[str, Any]) -> bool:
        expected = pending.get("expected", {})
        if not expected:
            return pending.get("movement") == "stopped"
        state = device.get("state", {})
        for key, value in expected.items():
            actual = state.get(key)
            if key in ("pos", "level"):
                try:
                    actual_number = float(actual)
                    if not math.isfinite(actual_number) or abs(actual_number - float(value)) > 1:
                        return False
                except (TypeError, ValueError):
                    return False
            elif str(actual).lower() != str(value).lower():
                return False
        return True

    @staticmethod
    def _cover_position(device: Dict[str, Any]) -> Optional[float]:
        try:
            value = device.get("state", {}).get("pos")
            if isinstance(value, bool):
                return None
            position = float(value)
            return position if math.isfinite(position) and 0 <= position <= 100 else None
        except (TypeError, ValueError):
            return None

    def _reconcile_pending(self, sid: str, device: Dict[str, Any]):
        pending = self.pending_commands.get(sid)
        if "blind" in device.get("data", "").lower():
            position = self._cover_position(device)
            previous = self._cover_position(self.devices.get(sid, {}))
            movement = None
            if position is not None:
                if pending and self._pending_matches(pending, device):
                    movement = "open" if position == 0 else "closed" if position == 100 else "stopped"
                elif pending and pending.get("movement") == "stopped":
                    movement = "stopped"
                elif previous is not None and position != previous:
                    # Increasing raw MiniSafe position means closing, unlike HA percent.
                    movement = ("open" if position == 0 else "closed" if position == 100
                                else "closing" if position > previous else "opening")
                elif pending and time.monotonic() - pending["timestamp"] < 2:
                    # A scheduled poll immediately after SendSC may still contain old data.
                    movement = pending.get("movement")
                if movement is None:
                    movement = "open" if position == 0 else "closed" if position == 100 else "stopped"
                if not hasattr(self, "_cover_movements"):
                    self._cover_movements = {}
                self._cover_movements[sid] = movement
                logger.debug("Cover poll %s: raw_pos=%s previous=%s movement=%s pending_age=%s",
                             sid, position, previous, movement,
                             round(time.monotonic() - pending["timestamp"], 1) if pending else None)
        if not pending:
            return
        age = time.monotonic() - pending["timestamp"]
        if self._pending_matches(pending, device):
            logger.debug(f"Command confirmed by MiniSafe2 for {sid}: {pending['command']}")
            self.pending_commands.pop(sid, None)
        elif age >= self._command_timeout:
            logger.warning(f"Command not confirmed for {sid}: {pending['command']}")
            self.pending_commands.pop(sid, None)

    def _is_recently_commanded(self, sid: str) -> bool:
        if self._recently_commanded_device != sid:
            return False
        last = self._last_command_time.get(sid, 0)
        if last and time.monotonic() - last < self._command_timeout:
            return True
        self._recently_commanded_device = None
        return False

    async def fetch_device_states(self):
        url = f"{self.base_url}?XC_FNC=GetStates&XC_PASS={base.quote_plus(self.password)}"
        try:
            # This also spaces startup's two GetStates calls. Never sleep holding the
            # lock: commands must not wait for the next scheduled poll.
            while True:
                async with self.minisafe_lock:
                    now = time.monotonic()
                    last = self._last_poll_started
                    delay = 0 if last is None else self.poll_interval - (now - last)
                    if delay <= 0:
                        self._last_poll_started = now
                        logger.debug("GetStates started; interval_since_previous=%s",
                                     round(now - last, 2) if last is not None else None)
                        async with self.session.get(url) as response:
                            if response.status == 200:
                                text = await response.text()
                                if text.startswith("{XC_SUC}"):
                                    devices = json.loads(text[8:])
                                    logger.debug("GetStates completed in %.2fs; devices=%s",
                                                 time.monotonic() - now, len(devices))
                                    return devices
                                logger.error("Unexpected GetStates response prefix")
                            else:
                                logger.error("GetStates HTTP error %s", response.status)
                        return None
                await asyncio.sleep(delay)
        except Exception as exc:
            logger.error("Error fetching device states: %s", type(exc).__name__)
        return None

    async def publish_device_state(self, sid: str, device: Dict[str, Any]):
        if "blind" not in device.get("data", "").lower():
            await super().publish_device_state(sid, device)
            return
        position = self._cover_position(device)
        if position is None:
            logger.warning("Ignoring missing/invalid MiniSafe cover position for %s", sid)
            return
        # Copy only for safe publication; never replace the real cached state with a target.
        normalized = dict(device, state=dict(device.get("state", {}), pos=position))
        await super().publish_device_state(sid, normalized)
        # Pending is diagnostic, not an authority for polled UI state.
        movement = getattr(self, "_cover_movements", {}).get(sid)
        movement = movement or ("open" if position == 0 else "closed" if position == 100 else "stopped")
        self.mqtt_client.publish(f"eltako/{sid}/movement", movement, retain=False)

    async def publish_discovery(self):
        await super().publish_discovery()
        for sid, device in self.devices.items():
            device_type = device.get("data", "").lower()
            device_info = {"identifiers": [f"eltako_{sid}"], "name": f"Eltako {sid}", "model": device.get("data", ""), "manufacturer": "Eltako", "via_device": "eltako_minisafe2"}
            if "blind" in device_type:
                config = {"name": f"Eltako Blind {sid}", "unique_id": f"eltako_blind_{sid}", "device_class": "blind", "command_topic": f"eltako/{sid}/set", "state_topic": f"eltako/{sid}/movement", "position_topic": f"eltako/{sid}/state", "set_position_topic": f"eltako/{sid}/set", "set_position_template": "{{ position }}", "position_closed": 100, "position_open": 0, "payload_open": "open", "payload_close": "close", "payload_stop": "stop", "state_open": "open", "state_opening": "opening", "state_closed": "closed", "state_closing": "closing", "state_stopped": "stopped", "optimistic": False, "device": device_info}
                self.mqtt_client.publish(f"homeassistant/cover/eltako_blind_{sid}/config", json.dumps(config), retain=True)
            elif self.is_switch_device(device_type):
                config = {"name": f"Eltako Switch {sid}", "unique_id": f"eltako_switch_{sid}", "command_topic": f"eltako/{sid}/set", "state_topic": f"eltako/{sid}/state", "payload_on": "on", "payload_off": "off", "optimistic": True, "device": device_info}
                self.mqtt_client.publish(f"homeassistant/switch/eltako_switch_{sid}/config", json.dumps(config), retain=True)
            elif "dimmer" in device_type:
                config = {"name": f"Eltako Dimmer {sid}", "unique_id": f"eltako_dimmer_{sid}", "command_topic": f"eltako/{sid}/set", "state_topic": f"eltako/{sid}/state", "brightness_command_topic": f"eltako/{sid}/set", "brightness_state_topic": f"eltako/{sid}/brightness", "brightness_scale": 255, "payload_on": "on", "payload_off": "off", "optimistic": True, "device": device_info}
                self.mqtt_client.publish(f"homeassistant/light/eltako_dimmer_{sid}/config", json.dumps(config), retain=True)

    async def poll_devices(self):
        while self.running:
            try:
                devices = await self.fetch_device_states()
                if devices:
                    for device in devices:
                        sid = device.get("sid")
                        if sid:
                            self._reconcile_pending(sid, device)
                            self.devices[sid] = device
                            await self.publish_device_state(sid, device)
                            self._log_device_feedback(sid, device)
                # fetch_device_states owns scheduling; no extra completion+interval sleep.
            except Exception as exc:
                logger.error(f"Polling error: {exc}")
                await asyncio.sleep(self.poll_interval)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 eltako2mqtt_experimental.py <config_file>")
        raise SystemExit(1)
    asyncio.run(ExperimentalBridge(sys.argv[1]).run())
