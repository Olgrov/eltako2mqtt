#!/usr/bin/with-contenv bashio

set -e

# Configuration
CONFIG_PATH=/data/options.json
OUTPUT_CONFIG=/config/eltako2mqtt/options.yaml

# Create config directory if it doesn't exist
mkdir -p /config/eltako2mqtt

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
cat > "${OUTPUT_CONFIG}" << 'EOF'
eltako:
  host: "ELTAKO_HOST_PLACEHOLDER"
  password: "ELTAKO_PASSWORD_PLACEHOLDER"
  poll_interval: ELTAKO_POLL_INTERVAL_PLACEHOLDER

mqtt:
  host: "MQTT_HOST_PLACEHOLDER"
  port: MQTT_PORT_PLACEHOLDER
  client_id: "MQTT_CLIENT_ID_PLACEHOLDER"
EOF

# Replace placeholders with actual values
sed -i "s|ELTAKO_HOST_PLACEHOLDER|${ELTAKO_HOST}|g" "${OUTPUT_CONFIG}"
sed -i "s|ELTAKO_PASSWORD_PLACEHOLDER|${ELTAKO_PASSWORD}|g" "${OUTPUT_CONFIG}"
sed -i "s|ELTAKO_POLL_INTERVAL_PLACEHOLDER|${ELTAKO_POLL_INTERVAL}|g" "${OUTPUT_CONFIG}"
sed -i "s|MQTT_HOST_PLACEHOLDER|${MQTT_HOST}|g" "${OUTPUT_CONFIG}"
sed -i "s|MQTT_PORT_PLACEHOLDER|${MQTT_PORT}|g" "${OUTPUT_CONFIG}"
sed -i "s|MQTT_CLIENT_ID_PLACEHOLDER|${MQTT_CLIENT_ID}|g" "${OUTPUT_CONFIG}"

# Add MQTT credentials if provided with proper indentation
if ! bashio::var.is_empty "${MQTT_USERNAME}"; then
    sed -i "/client_id:/a\  username: \"${MQTT_USERNAME}\"" "${OUTPUT_CONFIG}"
fi

if ! bashio::var.is_empty "${MQTT_PASSWORD}"; then
    sed -i "/client_id:/a\  password: \"${MQTT_PASSWORD}\"" "${OUTPUT_CONFIG}"
fi

# Set log level
export PYTHONPATH="/usr/lib/python3.11/site-packages"
if [[ "${LOG_LEVEL}" == "DEBUG" ]]; then
    export PYTHONUNBUFFERED=1
fi

bashio::log.info "Eltako Host: ${ELTAKO_HOST}"
bashio::log.info "MQTT Host: ${MQTT_HOST}:${MQTT_PORT}"
bashio::log.info "Config file created at: ${OUTPUT_CONFIG}"
bashio::log.info "Starting Python bridge..."

# Debug: Show config file content
bashio::log.debug "Config file content:"
bashio::log.debug "$(cat ${OUTPUT_CONFIG})"

# Start the Python script
exec python3 /eltako2mqtt.py "${OUTPUT_CONFIG}"
