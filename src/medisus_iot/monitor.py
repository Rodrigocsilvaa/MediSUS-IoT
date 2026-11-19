"""MQTT subscriber that validates, records, and reports temperature readings."""

import json
import logging
import math
import os
import signal
import threading

import paho.mqtt.client as mqtt

from medisus_iot.readings import is_out_of_range, parse_reading, validate_thresholds
from medisus_iot.storage import ReadingStore


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("medisus_iot.monitor")


def _environment_float(name: str, default: str) -> float:
    try:
        value = float(os.getenv(name, default))
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def main() -> None:
    min_temp_c, max_temp_c = validate_thresholds(
        _environment_float("MIN_TEMP_C", "2"),
        _environment_float("MAX_TEMP_C", "8"),
    )
    host = os.getenv("MQTT_HOST", "localhost")
    port = int(os.getenv("MQTT_PORT", "1883"))
    topic = os.getenv("MQTT_TOPIC", "medisus/ubs/+/temperatura")
    store = ReadingStore(os.getenv("DATABASE_PATH", "readings.sqlite3"))
    stop_event = threading.Event()

    def on_connect(client, userdata, flags, reason_code, properties) -> None:
        if reason_code.is_failure:
            logger.error("Falha ao conectar ao broker MQTT: %s", reason_code)
            return
        logger.info("Conectado ao broker %s:%s; assinando %s", host, port, topic)
        client.subscribe(topic, qos=1)

    def on_message(client, userdata, message) -> None:
        try:
            reading = parse_reading(message.payload)
        except ValueError as exc:
            logger.warning("Leitura rejeitada no tópico %s: %s", message.topic, exc)
            return

        alert = is_out_of_range(reading, min_temp_c, max_temp_c)
        store.record(reading, alert)
        event = {
            "device_id": reading.device_id,
            "temperature_c": reading.temperature_c,
            "timestamp": reading.timestamp,
            "alert": alert,
        }
        logger.log(
            logging.WARNING if alert else logging.INFO,
            "%s",
            json.dumps(event, ensure_ascii=True),
        )

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="medisus-iot-monitor",
    )
    client.on_connect = on_connect
    client.on_message = on_message

    def request_stop(signum: int, frame: object) -> None:
        stop_event.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    try:
        client.connect(host, port, keepalive=60)
        client.loop_start()
        stop_event.wait()
    finally:
        client.disconnect()
        client.loop_stop()
        store.close()


if __name__ == "__main__":
    main()
