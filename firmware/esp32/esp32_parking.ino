#include <WiFi.h>
#include <PubSubClient.h>

const char* WIFI_SSID = "YOUR_WIFI";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";
const char* MQTT_HOST = "192.168.1.100";
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC = "parking/slots";

const int SENSOR_PINS[4] = {25, 26, 27, 14};
const int LED_PINS[4] = {16, 17, 18, 19};
const char* SLOT_NAMES[4] = {"SLOT-1", "SLOT-2", "SLOT-3", "SLOT-4"};

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
bool lastState[4] = {false, false, false, false};
unsigned long lastChange[4] = {0, 0, 0, 0};
const unsigned long DEBOUNCE_MS = 150;

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) delay(300);
}

void connectMQTT() {
  while (!mqtt.connected()) {
    String clientId = "ESP32-PARKING-" + String((uint32_t)ESP.getEfuseMac(), HEX);
    if (mqtt.connect(clientId.c_str())) return;
    delay(1000);
  }
}

void publishState(int index, bool occupied) {
  String payload = "{\"slot\":\"" + String(SLOT_NAMES[index]) +
                   "\",\"occupied\":" + String(occupied ? "true" : "false") +
                   ",\"source\":\"ir\",\"confidence\":1.0,\"device_id\":\"ESP32-01\"}";
  mqtt.publish(MQTT_TOPIC, payload.c_str(), true);
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 4; i++) {
    pinMode(SENSOR_PINS[i], INPUT);
    pinMode(LED_PINS[i], OUTPUT);
  }
  connectWiFi();
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();
  if (!mqtt.connected()) connectMQTT();
  mqtt.loop();

  for (int i = 0; i < 4; i++) {
    bool occupied = digitalRead(SENSOR_PINS[i]) == LOW;
    digitalWrite(LED_PINS[i], occupied ? LOW : HIGH);

    if (occupied != lastState[i] && millis() - lastChange[i] > DEBOUNCE_MS) {
      lastState[i] = occupied;
      lastChange[i] = millis();
      publishState(i, occupied);
    }
  }
  delay(20);
}