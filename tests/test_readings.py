import json
import unittest

from medisus_iot.readings import (
    Reading,
    is_out_of_range,
    parse_reading,
    validate_thresholds,
)


class ParseReadingTests(unittest.TestCase):
    def test_normalizes_timezone_and_accepts_temperature(self):
        reading = parse_reading(
            json.dumps(
                {
                    "device_id": "  sensor-1 ",
                    "temperature_c": 4.5,
                    "timestamp": "2026-01-01T09:00:00-03:00",
                }
            )
        )
        self.assertEqual(reading.device_id, "sensor-1")
        self.assertEqual(reading.temperature_c, 4.5)
        self.assertEqual(reading.timestamp, "2026-01-01T12:00:00+00:00")

    def test_rejects_missing_timezone(self):
        payload = '{"device_id":"sensor-1","temperature_c":4,"timestamp":"2026-01-01T12:00:00"}'
        with self.assertRaisesRegex(ValueError, "timezone"):
            parse_reading(payload)

    def test_rejects_boolean_and_out_of_sensor_range(self):
        for temperature in (True, 126, 10**400):
            payload = json.dumps(
                {
                    "device_id": "sensor-1",
                    "temperature_c": temperature,
                    "timestamp": "2026-01-01T12:00:00Z",
                }
            )
            with self.subTest(temperature=temperature), self.assertRaises(ValueError):
                parse_reading(payload)

    def test_rejects_non_object_json(self):
        with self.assertRaisesRegex(ValueError, "JSON object"):
            parse_reading("[]")


class ThresholdTests(unittest.TestCase):
    def test_alerts_only_outside_configured_range(self):
        self.assertFalse(is_out_of_range(Reading("s", 2, "t"), 2, 8))
        self.assertFalse(is_out_of_range(Reading("s", 8, "t"), 2, 8))
        self.assertTrue(is_out_of_range(Reading("s", 8.1, "t"), 2, 8))
        self.assertTrue(is_out_of_range(Reading("s", 1.9, "t"), 2, 8))

    def test_rejects_invalid_thresholds(self):
        with self.assertRaisesRegex(ValueError, "lower"):
            validate_thresholds(8, 2)


if __name__ == "__main__":
    unittest.main()
