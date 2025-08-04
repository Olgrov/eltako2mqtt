#!/usr/bin/with-contenv bashio

set -e

# Configuration
CONFIG_PATH=/data/options.json

# Parse configuration
ELTAKO_HOST=$(bashio::config 'eltako.host')
ELTAKO_PASSWORD=$(bashio::config 'eltako.password')
ELTAKO_POLL_INTERVAL=$(bashio::config 'eltako.poll_interval')
MQTT_HOST=$(bashio::config 'mqtt.host')
MQTT_PORT=$(bashio::config 'mqtt.port')
MQTT_USERNAME=$(bashio::config 'mqtt.username')
MQTT_PASSWORD=$(bashio::config 'mqtt.password')
MQTT_CLIENT_ID=$(bashio::config 'mqtt.client_id')
LOG_LEVEL=$(bashio::config 'logging.level')

bashio::log.info "Starting Eltako2MQTT Bridge..."

# Validate required configuration
if bashio::var.is_empty "${ELTAKO_HOST}"; then
    bashio::log.fatal "Eltako host is required but not configured!"
    bashio::exit.nok
fi

if bashio::var.is_empty "${ELTAKO_PASSWORD}"; then
    bashio::log.fatal "Eltako password is required but not configured!"
    bashio::exit.nok
fi

if bashio::var.is_empty "${MQTT_HOST}"; then
    bashio::log.fatal "MQTT host is required but not configured!"
    bashio::exit.nok
fi

# Create configuration file for the Python script
cat > /tmp/eltako2mqtt.yaml << EOF
eltako:
  host: "${ELTAKO_HOST}"
  password: "${ELTAKO_PASSWORD}"
  poll_interval: ${ELTAKO_POLL_INTERVAL}

mqtt:
  host: "${MQTT_HOST}"
  port: ${MQTT_PORT}
  client_id: "${MQTT_CLIENT_ID}"
EOF

# Add MQTT credentials if provided
if ! bashio::var.is_empty "${MQTT_USERNAME}"; then
    echo "  username: "${MQTT_USERNAME}"" >> /tmp/eltako2mqtt.yaml
fi

if ! bashio::var.is_empty "${MQTT_PASSWORD}"; then
    echo "  password: "${MQTT_PASSWORD}"" >> /tmp/eltako2mqtt.yaml
fi

# Set log level
export PYTHONPATH="/usr/lib/python3.11/site-packages"
if [[ "${LOG_LEVEL}" == "DEBUG" ]]; then
    export PYTHONUNBUFFERED=1
fi

bashio::log.info "Eltako Host: ${ELTAKO_HOST}"
bashio::log.info "MQTT Host: ${MQTT_HOST}:${MQTT_PORT}"
bashio::log.info "Starting Python bridge..."

# Start the Python script
exec python3 /eltako2mqtt.py /tmp/eltako2mqtt.yaml
