/*
  MediSUS IoT temperature sensor reference.
  Libraries: PubSubClient, OneWire, DallasTemperature.
  Configure credentials locally; never commit real secrets.
  This sketch has not been validated on physical hardware.
*/
#include <WiFi.h>
#include <PubSubClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <time.h>

const char *WIFI_SSID = "PREENCHER_WIFI";
const char *WIFI_PASSWORD = "PREENCHER_SENHA";
const char *MQTT_SERVER = "192.168.1.10";
const int MQTT_PORT = 1883;
const char *DEVICE_ID = "esp32-ubs-demo";
const char *MQTT_TOPIC = "medisus/ubs/demo/temperatura";
const int ONE_WIRE_PIN = 4;

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
OneWire oneWire(ONE_WIRE_PIN);
DallasTemperature sensor(&oneWire);

void connectWifi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void connectMqtt() {
  while (!mqttClient.connected()) {
    if (mqttClient.connect(DEVICE_ID)) {
      return;
    }
    delay(2000);
  }
}

void setup() {
  Serial.begin(115200);
  sensor.begin();
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  connectWifi();
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  while (time(nullptr) < 1700000000) {
    delay(500);
  }
  connectMqtt();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWifi();
  }
  if (!mqttClient.connected()) {
    connectMqtt();
  }

  sensor.requestTemperatures();
  const float temperatureC = sensor.getTempCByIndex(0);
  if (temperatureC != DEVICE_DISCONNECTED_C) {
    char payload[192];
    char timestamp[25];
    const time_t now = time(nullptr);
    struct tm utcTime;
    gmtime_r(&now, &utcTime);
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", &utcTime);
    snprintf(
      payload,
      sizeof(payload),
      "{\"device_id\":\"%s\",\"temperature_c\":%.2f,\"timestamp\":\"%s\"}",
      DEVICE_ID,
      temperatureC,
      timestamp
    );
    mqttClient.publish(MQTT_TOPIC, payload);
    Serial.println(payload);
  }

  mqttClient.loop();
  delay(10000);
}
