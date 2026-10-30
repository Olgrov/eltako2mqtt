#!/usr/bin/with-contenv bashio
set -e
CONFIG_PATH=/data/options.json
ELTAKO_HOST=$(bashio::config 'eltako.host')
ELTAKO_PASSWORD=$(bashio::config 'eltako.password')
ELTAKO_POLL_INTERVAL=$(bashio::config 'eltako.poll_interval')
COMMAND_FEEDBACK_TIMEOUT=120
if bashio::config.has_value 'eltako.command_feedback_timeout'; then
    COMMAND_FEEDBACK_TIMEOUT=$(bashio::config 'eltako.command_feedback_timeout')
fi
MQTT_HOST=$(bashio::config 'mqtt.host')
MQTT_PORT=$(bashio::config 'mqtt.port')
MQTT_USERNAME=$(bashio::config 'mqtt.username')
MQTT_PASSWORD=$(bashio::config 'mqtt.password')
MQTT_CLIENT_ID=$(bashio::config 'mqtt.client_id')
LOG_LEVEL=$(bashio::config 'logging.level')
cat > /tmp/eltako2mqtt.yaml << EOF
eltako:
  host: "${ELTAKO_HOST}"
  password: "${ELTAKO_PASSWORD}"
  poll_interval: ${ELTAKO_POLL_INTERVAL}
  command_feedback_timeout: ${COMMAND_FEEDBACK_TIMEOUT}
mqtt:
  host: "${MQTT_HOST}"
  port: ${MQTT_PORT}
  client_id: "${MQTT_CLIENT_ID}"
logging:
  level: "${LOG_LEVEL}"
EOF
if ! bashio::var.is_empty "${MQTT_USERNAME}"; then sed -i "/^mqtt:/a\\  username: \"${MQTT_USERNAME}\"" /tmp/eltako2mqtt.yaml; fi
if ! bashio::var.is_empty "${MQTT_PASSWORD}"; then sed -i "/username:/a\\  password: \"${MQTT_PASSWORD}\"" /tmp/eltako2mqtt.yaml; fi
export PYTHONPATH="/usr/lib/python3.11/site-packages"
export PYTHONUNBUFFERED=1
bashio::log.warning "Starting experimental optimistic-state bridge"
exec python3 /eltako2mqtt_experimental.py /tmp/eltako2mqtt.yaml
