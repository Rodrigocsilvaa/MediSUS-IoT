"""SQLite persistence for validated readings."""

import sqlite3
from pathlib import Path

from medisus_iot.readings import Reading


class ReadingStore:
    def __init__(self, database_path: str) -> None:
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(database_path)
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY,
                device_id TEXT NOT NULL,
                temperature_c REAL NOT NULL,
                timestamp TEXT NOT NULL,
                alert INTEGER NOT NULL
            )
            """
        )
        self._connection.commit()

    def record(self, reading: Reading, alert: bool) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO readings (device_id, temperature_c, timestamp, alert)
                VALUES (?, ?, ?, ?)
                """,
                (reading.device_id, reading.temperature_c, reading.timestamp, int(alert)),
            )

    def close(self) -> None:
        self._connection.close()
