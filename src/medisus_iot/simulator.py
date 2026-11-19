"""Publish a short sequence of synthetic temperature readings over MQTT."""

from datetime import datetime, timezone
import json
import os
import time

import paho.mqtt.client as mqtt


def main() -> None:
    host = os.getenv("MQTT_HOST", "localhost")
    port = int(os.getenv("MQTT_PORT", "1883"))
    topic = os.getenv("MQTT_TOPIC", "medisus/ubs/demo/temperatura")
    interval = float(os.getenv("SIMULATOR_INTERVAL_SECONDS", "1"))
    if interval < 0:
        raise ValueError("SIMULATOR_INTERVAL_SECONDS cannot be negative")

    temperatures = (4.5, 5.2, 8.3, 3.8)
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="medisus-iot-simulator",
    )
    client.connect(host, port, keepalive=60)
    client.loop_start()
    try:
        for temperature in temperatures:
            payload = json.dumps(
                {
                    "device_id": "simulador-ubs-demo",
                    "temperature_c": temperature,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            result = client.publish(topic, payload, qos=1)
            result.wait_for_publish()
            print(f"Publicado dado sintético: {payload}", flush=True)
            time.sleep(interval)
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()
