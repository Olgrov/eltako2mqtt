ARG BUILD_FROM

FROM $BUILD_FROM

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN \
  apk add --no-cache \
    python3=~3.11 \
    py3-pip=~23.1

COPY requirements.txt /requirements.txt
RUN pip3 install --no-cache-dir -r /requirements.txt

# The tested state-feedback implementation is the production entry point.
COPY run.sh /run.sh
COPY eltako2mqtt.py /
COPY bridge_base.py /
COPY state_feedback.py /

RUN chmod a+x /run.sh

LABEL \
  io.hass.name="Eltako2MQTT" \
  io.hass.description="Eltako MiniSafe2 to MQTT Bridge for Home Assistant" \
  io.hass.arch="armhf|aarch64|i386|amd64|armv7" \
  io.hass.type="addon" \
  io.hass.version="1.3.0"

CMD [ "/run.sh" ]
