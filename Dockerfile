ARG BUILD_FROM

FROM $BUILD_FROM

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN \
  apk add --no-cache \
    python3=~3.11 \
    py3-pip=~23.1 \
    py3-yaml=~6.0 \
  && pip3 install --no-cache-dir \
    aiohttp==3.14.5 \
    paho-mqtt==2.1.0 \
    PyYAML==6.0.3

# The tested state-feedback implementation is the production entry point.
COPY run.sh /run.sh
COPY eltako2mqtt.py /
COPY state_feedback.py /
COPY requirements.txt /

RUN chmod a+x /run.sh

LABEL \
  io.hass.name="Eltako2MQTT" \
  io.hass.description="Eltako MiniSafe2 to MQTT Bridge for Home Assistant" \
  io.hass.arch="armhf|aarch64|i386|amd64|armv7" \
  io.hass.type="addon" \
  io.hass.version="1.3.0"

CMD [ "/run.sh" ]
