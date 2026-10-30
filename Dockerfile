ARG BUILD_FROM

FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install requirements for add-on
RUN \
  apk add --no-cache \
    python3=~3.11 \
    py3-pip=~23.1 \
    py3-yaml=~6.0 \
  && pip3 install --no-cache-dir \
    aiohttp==3.14.5 \
    paho-mqtt==2.1.0 \
    PyYAML==6.0.3

# Copy production and experimental bridge files
COPY run-experimental.sh /run-experimental.sh
COPY eltako2mqtt.py /
COPY eltako2mqtt_experimental.py /
COPY requirements.txt /

RUN chmod a+x /run-experimental.sh

# Labels
LABEL \
  io.hass.name="Eltako2MQTT Experimental" \
  io.hass.description="Eltako MiniSafe2 bridge with optimistic Home Assistant feedback" \
  io.hass.arch="armhf|aarch64|i386|amd64|armv7" \
  io.hass.type="addon" \
  io.hass.version="1.2.5-test.3"

CMD [ "/run-experimental.sh" ]
