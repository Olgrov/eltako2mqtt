#!/usr/bin/with-contenv bashio
set -euo pipefail

# Read Supervisor JSON directly: YAML interpolation/sed can corrupt passwords
# containing quotes, backslashes, newlines, or shell metacharacters.
# Validate this same local input rather than asking Bashio for Supervisor API
# options; startup does not require Supervisor API access.
umask 077
python3 - <<'PY'
import json
import yaml

with open("/data/options.json", encoding="utf-8") as source:
    options = json.load(source)

for section, key in (("eltako", "host"), ("eltako", "password"), ("mqtt", "host")):
    values = options.get(section) if isinstance(options, dict) else None
    if not isinstance(values, dict) or values.get(key) in (None, ""):
        raise SystemExit(f"Required option {section}.{key} is not configured")

config = {
    "eltako": {
        "poll_interval": 30,
        "command_feedback_timeout": 120,
        **options["eltako"],
    },
    "mqtt": {"port": 1883, "client_id": "eltako2mqtt", **options["mqtt"]},
    "logging": {"level": "INFO", **options.get("logging", {})},
}
with open("/tmp/eltako2mqtt.yaml", "w", encoding="utf-8") as target:
    yaml.safe_dump(config, target, allow_unicode=True)
PY

export PYTHONUNBUFFERED=1
bashio::log.info "Starting Eltako2MQTT v1.4.0 with command-state feedback"
exec python3 /eltako2mqtt.py /tmp/eltako2mqtt.yaml
