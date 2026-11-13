#!/usr/bin/env python3
"""Production entry point for Eltako2MQTT v1.4.0 (64-bit platforms)."""

import asyncio
import sys

from state_feedback import StateFeedbackBridge

# Preserve the public class import while always selecting production feedback.
EltakoMiniSafe2Bridge = StateFeedbackBridge


async def main():
    if len(sys.argv) != 2:
        print("Usage: python3 eltako2mqtt.py <config_file>")
        raise SystemExit(1)
    await EltakoMiniSafe2Bridge(sys.argv[1]).run()


if __name__ == "__main__":
    asyncio.run(main())
