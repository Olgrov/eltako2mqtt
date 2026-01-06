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
    aiohttp==3.8.5 \
    paho-mqtt==1.6.1 \
    requests

# Copy data for add-on
COPY run.sh /
COPY eltako2mqtt.py /
COPY requirements.txt /

RUN chmod a+x /run.sh

# Labels
LABEL \
  io.hass.name="Eltako2MQTT" \
  io.hass.description="Eltako MiniSafe2 to MQTT Bridge" \
  io.hass.arch="armhf|aarch64|i386|amd64|armv7" \
  io.hass.type="addon" \
  io.hass.version="1.0.0"

CMD [ "/run.sh" ]