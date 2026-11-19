import json
import unittest
from io import BytesIO
from unittest.mock import patch

from medisus_iot.ai_summary import API_URL, generate_summary


class GenerateSummaryTests(unittest.TestCase):
    def test_sends_readings_to_ai_and_returns_summary(self):
        readings = [
            {
                "temperature_c": 8.3,
                "timestamp": "2026-01-01T12:00:00+00:00",
                "alert": True,
            }
        ]
        response_body = json.dumps(
            {"choices": [{"message": {"content": "Uma leitura foi marcada como alerta."}}]}
        ).encode("utf-8")
        response = BytesIO(response_body)

        with patch("medisus_iot.ai_summary.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__.return_value = response
            summary = generate_summary(readings, "test-key")

        request = mock_urlopen.call_args.args[0]
        self.assertEqual(summary, "Uma leitura foi marcada como alerta.")
        self.assertEqual(request.full_url, API_URL)
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        sent = json.loads(request.data.decode("utf-8"))
        self.assertEqual(sent["messages"][1]["content"], json.dumps({"readings": readings}))

    def test_rejects_missing_api_key_and_empty_readings(self):
        with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
            generate_summary([], "")
        with self.assertRaisesRegex(ValueError, "no readings"):
            generate_summary([], "test-key")

    def test_rejects_response_without_summary(self):
        response = BytesIO(b'{"choices":[]}')
        with patch("medisus_iot.ai_summary.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__.return_value = response
            with self.assertRaisesRegex(RuntimeError, "did not contain a summary"):
                generate_summary([{"temperature_c": 4.5, "alert": False}], "test-key")


if __name__ == "__main__":
    unittest.main()
