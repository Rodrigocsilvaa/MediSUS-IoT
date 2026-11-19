import sqlite3
import tempfile
import unittest
from pathlib import Path

from medisus_iot.readings import Reading
from medisus_iot.storage import ReadingStore


class ReadingStoreTests(unittest.TestCase):
    def test_records_reading_and_alert_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "nested" / "readings.sqlite3"
            store = ReadingStore(str(database))
            store.record(Reading("sensor-1", 8.5, "2026-01-01T12:00:00+00:00"), True)
            store.close()

            connection = sqlite3.connect(database)
            try:
                row = connection.execute(
                    "SELECT device_id, temperature_c, alert FROM readings"
                ).fetchone()
            finally:
                connection.close()
            self.assertEqual(row, ("sensor-1", 8.5, 1))

    def test_latest_readings_are_chronological_and_do_not_include_device_id(self):
        store = ReadingStore(":memory:")
        store.record(Reading("private-device-name", 4.5, "2026-01-01T12:00:00+00:00"), False)
        store.record(Reading("private-device-name", 8.5, "2026-01-01T12:01:00+00:00"), True)

        latest = store.latest_readings(limit=1)

        self.assertEqual(
            latest,
            [
                {
                    "temperature_c": 8.5,
                    "timestamp": "2026-01-01T12:01:00+00:00",
                    "alert": True,
                }
            ],
        )
        store.close()


if __name__ == "__main__":
    unittest.main()
