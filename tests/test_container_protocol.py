import io
import json
import socket
import tarfile
import unittest

from container_smoke import mqtt_packet, options_archive, read_exact


class ContainerSmokeContracts(unittest.TestCase):
    def test_short_mqtt_packet(self):
        self.assertEqual(mqtt_packet(0x30, b"abc"), b"\x30\x03abc")

    def test_multibyte_mqtt_length(self):
        packet = mqtt_packet(0x30, b"x" * 300)
        self.assertEqual(packet[:3], b"\x30\xac\x02")
        self.assertEqual(len(packet), 303)

    def test_socket_reader_and_eof(self):
        left, right = socket.socketpair()
        try:
            left.sendall(b"abc")
            self.assertEqual(read_exact(right, 3), b"abc")
            left.close()
            with self.assertRaises(EOFError):
                read_exact(right, 1)
        finally:
            left.close()
            right.close()

    def test_options_stay_in_memory_and_receive_private_permissions(self):
        options = {"eltako": {"host": "127.0.0.1"}, "mqtt": {"port": 1883}}
        with tarfile.open(fileobj=io.BytesIO(options_archive(options))) as archive:
            self.assertEqual(archive.getnames(), ["data", "data/options.json"])
            self.assertEqual(archive.getmember("data").mode, 0o700)
            self.assertEqual(archive.getmember("data/options.json").mode, 0o600)
            self.assertEqual(json.load(archive.extractfile("data/options.json")), options)
