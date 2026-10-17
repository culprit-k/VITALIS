/*
 * VITALIS synthetic gateway — ESP32-S3 bench firmware.
 * Generated values only. No sensors, patient connection, Wi-Fi, or storage.
 * Emits one JSON line per channel at 1 Hz over USB serial.
 */
#include <Arduino.h>
#include <math.h>

static uint32_t sequenceNumber = 0;
static const uint32_t PERIOD_MS = 1000;
static uint32_t nextFrameAt = 0;

void emitSample(const char* channel, float value, const char* unit) {
  Serial.print("{\"seq\":");
  Serial.print(sequenceNumber);
  Serial.print(",\"elapsed_ms\":");
  Serial.print(millis());
  Serial.print(",\"channel\":\"");
  Serial.print(channel);
  Serial.print("\",\"value\":");
  Serial.print(value, 2);
  Serial.print(",\"unit\":\"");
  Serial.print(unit);
  Serial.print("\",\"quality\":\"good\",\"source\":\"esp32-synthetic-v1\"}\n");
}

void setup() {
  Serial.begin(115200);
  const uint32_t waitStarted = millis();
  while (!Serial && millis() - waitStarted < 3000) {
    delay(10);
  }
  nextFrameAt = millis();
  Serial.println("{\"type\":\"vitalis_gateway_ready\",\"mode\":\"synthetic_only\",\"schema\":1}");
}

void loop() {
  const uint32_t now = millis();
  if ((int32_t)(now - nextFrameAt) < 0) {
    delay(2);
    return;
  }
  nextFrameAt = now + PERIOD_MS;

  // Deterministic, bounded toy signals for transport/software testing only.
  const float t = (float)now / 1000.0f;
  const float heartRate = 76.0f + 4.0f * sinf(t / 8.0f);
  const float spo2 = 97.0f + 0.6f * sinf(t / 13.0f);
  emitSample("heart_rate", heartRate, "bpm");
  emitSample("spo2", spo2, "%");
  sequenceNumber++;
}
