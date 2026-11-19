"""Validation and alert classification for temperature readings."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
from typing import Any


DS18B20_MIN_C = -55.0
DS18B20_MAX_C = 125.0


@dataclass(frozen=True)
class Reading:
    device_id: str
    temperature_c: float
    timestamp: str


def parse_reading(payload: bytes | str) -> Reading:
    """Parse JSON and require a timezone-aware ISO 8601 timestamp."""
    try:
        data: Any = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise ValueError("payload must be valid JSON") from exc

    if not isinstance(data, dict):
        raise ValueError("payload must be a JSON object")

    device_id = data.get("device_id")
    if not isinstance(device_id, str) or not device_id.strip() or len(device_id) > 100:
        raise ValueError("device_id must be a non-empty string of at most 100 characters")

    temperature = data.get("temperature_c")
    if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
        raise ValueError("temperature_c must be a number")
    try:
        temperature = float(temperature)
    except OverflowError as exc:
        raise ValueError("temperature_c is outside the DS18B20 range") from exc
    if not math.isfinite(temperature) or not DS18B20_MIN_C <= temperature <= DS18B20_MAX_C:
        raise ValueError("temperature_c is outside the DS18B20 range")

    timestamp = data.get("timestamp")
    if not isinstance(timestamp, str):
        raise ValueError("timestamp must be an ISO 8601 string")
    try:
        parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be an ISO 8601 string") from exc
    if parsed_timestamp.tzinfo is None or parsed_timestamp.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")

    return Reading(
        device_id=device_id.strip(),
        temperature_c=temperature,
        timestamp=parsed_timestamp.astimezone(timezone.utc).isoformat(),
    )


def validate_thresholds(min_temp_c: float, max_temp_c: float) -> tuple[float, float]:
    if not math.isfinite(min_temp_c) or not math.isfinite(max_temp_c):
        raise ValueError("temperature thresholds must be finite numbers")
    if min_temp_c >= max_temp_c:
        raise ValueError("MIN_TEMP_C must be lower than MAX_TEMP_C")
    return min_temp_c, max_temp_c


def is_out_of_range(reading: Reading, min_temp_c: float, max_temp_c: float) -> bool:
    return reading.temperature_c < min_temp_c or reading.temperature_c > max_temp_c
