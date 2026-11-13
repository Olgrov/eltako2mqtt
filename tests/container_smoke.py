#!/usr/bin/env python3
"""Exercise the real default container entrypoint against loopback-only fakes."""

import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import socket
import struct
import subprocess
import sys
import tarfile
import threading
import time
from urllib.parse import parse_qs, urlsplit
import uuid


def mqtt_packet(kind, body):
    length = len(body)
    encoded = bytearray([kind])
    while True:
        byte = length % 128
        length //= 128
        encoded.append(byte | (128 if length else 0))
        if not length:
            return bytes(encoded) + body


def read_exact(connection, size):
    data = bytearray()
    while len(data) < size:
        chunk = connection.recv(size - len(data))
        if not chunk:
            raise EOFError
        data.extend(chunk)
    return bytes(data)


class Broker:
    """Minimal MQTT 3.1.1 CONNECT/SUBSCRIBE/PUBLISH/PING test broker."""

    def __init__(self):
        self.listener = socket.socket()
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen(1)
        self.listener.settimeout(30)
        self.port = self.listener.getsockname()[1]
        self.connection = None
        self.send_lock = threading.Lock()
        self.condition = threading.Condition()
        self.messages = []
        self.subscriptions = 0
        self.error = None
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def send(self, packet):
        with self.send_lock:
            self.connection.sendall(packet)

    def run(self):
        try:
            connection, _ = self.listener.accept()
            self.connection = connection
            connection.settimeout(30)
            while True:
                kind = read_exact(connection, 1)[0] >> 4
                length, multiplier = 0, 1
                for _ in range(4):
                    byte = read_exact(connection, 1)[0]
                    length += (byte & 127) * multiplier
                    multiplier *= 128
                    if not byte & 128:
                        break
                else:
                    raise AssertionError("Malformed MQTT length")
                body = read_exact(connection, length)
                if kind == 1:
                    self.send(b"\x20\x02\x00\x00")
                elif kind == 8:
                    offset, count = 2, 0
                    while offset < len(body):
                        topic_length = struct.unpack("!H", body[offset:offset + 2])[0]
                        offset += 2 + topic_length + 1
                        count += 1
                    self.send(mqtt_packet(0x90, body[:2] + bytes(count)))
                    with self.condition:
                        self.subscriptions += count
                        self.condition.notify_all()
                elif kind == 3:
                    size = struct.unpack("!H", body[:2])[0]
                    topic = body[2:2 + size].decode()
                    payload = body[2 + size:].decode()
                    with self.condition:
                        self.messages.append((topic, payload))
                        self.condition.notify_all()
                elif kind == 12:
                    self.send(b"\xd0\x00")
                elif kind == 14:
                    return
        except (EOFError, OSError):
            return
        except Exception as exc:
            self.error = exc
            with self.condition:
                self.condition.notify_all()

    def wait(self, topic, predicate, after=0, timeout=40):
        end = time.monotonic() + timeout
        with self.condition:
            while True:
                if self.error:
                    raise AssertionError(f"Broker error: {self.error}")
                for current_topic, payload in self.messages[after:]:
                    if current_topic == topic and predicate(payload):
                        return payload
                remaining = end - time.monotonic()
                if remaining <= 0:
                    raise AssertionError(f"No expected publication on {topic}")
                self.condition.wait(remaining)

    def command(self, sid, payload):
        with self.condition:
            mark = len(self.messages)
        topic = f"eltako/{sid}/set".encode()
        self.send(mqtt_packet(0x30, struct.pack("!H", len(topic)) + topic + payload.encode()))
        return mark

    def close(self):
        if self.connection is not None:
            self.connection.close()
        self.listener.close()


class MiniSafe:
    def __init__(self):
        self.lock = threading.Lock()
        self.commands = []
        self.devices = [
            {"sid": "01", "adr": "cover", "data": "eltako_blind", "state": {"pos": 25}},
            {"sid": "13", "adr": "dimmer", "data": "eltako_dimmer", "state": {"state": "on", "level": 40}},
            {"sid": "20", "adr": "switch", "data": "eltako_switch", "state": {"state": "off"}},
            {"sid": "30", "adr": "smoke", "data": "eltako_tf_smoke", "state": {"smoke": False, "temperature": 21}},
            {"sid": "31", "adr": "weather", "data": "eltako_weather", "state": {"temperature": 19, "wind": 2, "rain_state": False, "s1": 1}},
        ]
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                query = parse_qs(urlsplit(self.path).query)
                if query.get("XC_PASS") != ["smoke-fixture"]:
                    self.send_error(403)
                    return
                with owner.lock:
                    if query.get("XC_FNC") == ["GetStates"]:
                        text = "{XC_SUC}" + json.dumps(copy.deepcopy(owner.devices))
                    elif query.get("XC_FNC") == ["SendSC"]:
                        address = query["address"][0]
                        command = query["data"][0]
                        owner.commands.append((address, command))
                        device = next(d for d in owner.devices if d["adr"] == address)
                        if address == "cover":
                            if command == "movedown":
                                device["state"]["pos"] = 100
                            elif command == "moveup":
                                device["state"]["pos"] = 0
                            elif command.startswith("moveTo"):
                                device["state"]["pos"] = int(command[6:])
                        elif address == "dimmer" and command.startswith("dimTo"):
                            device["state"].update(state="on", level=int(command[5:]))
                        elif address == "switch":
                            device["state"]["state"] = command
                        text = "{XC_SUC}"
                    else:
                        text = "{XC_ERR}"
                data = text.encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def options_archive(options):
    """Keep synthetic option fixtures in memory; Docker receives a private file."""
    content = json.dumps(options).encode()
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w") as archive:
        directory = tarfile.TarInfo("data")
        directory.type = tarfile.DIRTYPE
        directory.mode = 0o700
        archive.addfile(directory)
        target = tarfile.TarInfo("data/options.json")
        target.mode = 0o600
        target.size = len(content)
        archive.addfile(target, io.BytesIO(content))
    return output.getvalue()


def docker(*args, **kwargs):
    return subprocess.run(["docker", *args], check=True, **kwargs)


def main():
    image = sys.argv[1] if len(sys.argv) > 1 else "eltako2mqtt:ci"
    broker, minisafe = Broker(), MiniSafe()
    container = "eltako-smoke-" + uuid.uuid4().hex[:12]
    created = False
    try:
        options = {
            "eltako": {"host": f"127.0.0.1:{minisafe.port}", "password": "smoke-fixture", "poll_interval": 1, "command_feedback_timeout": 30},
            "mqtt": {"host": "127.0.0.1", "port": broker.port, "client_id": container},
            "logging": {"level": "INFO"},
        }
        docker("create", "--name", container, "--network", "host", image, capture_output=True)
        created = True
        docker("cp", "-", container + ":/", input=options_archive(options), capture_output=True)
        docker("start", container, capture_output=True)
        broker.wait("homeassistant/cover/eltako_blind_01/config", lambda p: json.loads(p)["optimistic"] is False)
        broker.wait("eltako/01/state", lambda p: float(p) == 25)
        broker.wait("eltako/30/smoke", lambda p: p == "false")
        broker.wait("eltako/31/illumination_east", lambda p: int(p) == 1000)
        assert broker.subscriptions >= 2

        mark = broker.command("01", "close")
        broker.wait("eltako/01/movement", lambda p: p == "closing", mark)
        broker.wait("eltako/01/state", lambda p: float(p) == 100, mark)
        mark = broker.command("01", "100")
        broker.wait("eltako/01/movement", lambda p: p == "opening", mark)
        broker.wait("eltako/01/state", lambda p: float(p) == 0, mark)
        mark = broker.command("01", "stop")
        broker.wait("eltako/01/movement", lambda p: p == "stopped", mark)
        mark = broker.command("13", "128")
        broker.wait("eltako/13/brightness", lambda p: int(p) == 128, mark)
        mark = broker.command("20", "on")
        broker.wait("eltako/20/state", lambda p: p == "on", mark)

        with minisafe.lock:
            assert minisafe.commands == [
                ("cover", "movedown"), ("cover", "moveTo0"), ("cover", "stop"),
                ("dimmer", "dimTo50"), ("switch", "on"),
            ], minisafe.commands
        docker("stop", "--time", "15", container, capture_output=True)
        result = docker("inspect", "--format", "{{.State.ExitCode}}", container, capture_output=True, text=True)
        assert result.stdout.strip() == "0", result.stdout
        logs = docker("logs", container, capture_output=True, text=True)
        assert "Eltako2MQTT 1.4.0;" in logs.stdout + logs.stderr
        print("PASS: default S6/Bashio entrypoint, MQTT discovery, real polls, cover close/slider/stop, dimmer, switch, sensors and clean shutdown.")
        print("Synthetic poll_interval=1 is test-only; production recommendation remains 30+ seconds.")
    except Exception:
        if created:
            subprocess.run(["docker", "logs", container], check=False)
        raise
    finally:
        if created:
            subprocess.run(["docker", "rm", "--force", container], capture_output=True, check=False)
        broker.close()
        minisafe.close()


if __name__ == "__main__":
    main()
