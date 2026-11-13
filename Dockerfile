ARG BUILD_FROM=ghcr.io/home-assistant/base-python:3.15-alpine3.24

FROM $BUILD_FROM

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY requirements.txt /requirements.txt
# Python and pip are provided by the official Home Assistant Python image.
# PyYAML may need a source build for the latest CPython; remove compilers after
# installation, retaining only the small libyaml runtime.
RUN apk upgrade --no-cache \
  && apk add --no-cache yaml \
  && apk add --no-cache --virtual .build-deps build-base yaml-dev \
  && python3 -m pip install --no-cache-dir -r /requirements.txt \
  && python3 -m pip check \
  && apk del .build-deps

# The tested state-feedback implementation is the production entry point.
COPY run.sh /run.sh
COPY eltako2mqtt.py /
COPY bridge_base.py /
COPY state_feedback.py /

RUN chmod a+x /run.sh

LABEL \
  io.hass.name="Eltako2MQTT" \
  io.hass.description="Eltako MiniSafe2 to MQTT Bridge for Home Assistant" \
  io.hass.arch="aarch64|amd64" \
  io.hass.type="addon" \
  io.hass.version="1.4.0"

CMD [ "/run.sh" ]
