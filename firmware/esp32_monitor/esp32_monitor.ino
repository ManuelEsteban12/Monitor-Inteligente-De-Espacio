/*
  Monitor Inteligente de Espacio — Firmware ESP32
  ------------------------------------------------
  Lee temperatura y humedad de un DHT11, las envía por WiFi al servidor,
  y activa un relé cuando el servidor reporta una alerta activa.

  Conexiones (según el armado físico del proyecto):
    DHT11  -> pin de datos en GPIO 4  (con resistencia pull-up entre datos y VCC)
    DHT11  -> VCC a 3V3, GND a GND
    Relé   -> pin IN en GPIO 26
    Relé   -> VCC y GND según el módulo (la mayoría acepta 5V o 3V3)

  Antes de compilar:
    1. Copia "config.h.example" a "config.h" en esta misma carpeta.
    2. Rellena tu SSID, contraseña de WiFi y la URL del servidor en config.h.
    3. NUNCA subas config.h a GitHub (ya está en .gitignore).

  Librerías necesarias (Arduino IDE > Administrador de librerías):
    - "DHT sensor library" de Adafruit
    - "Adafruit Unified Sensor" (dependencia de la anterior)
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

#include "config.h"   // define WIFI_SSID, WIFI_PASSWORD, SERVER_URL

#define DHTPIN 4
#define DHTTYPE DHT11
#define RELAY_PIN 26

DHT dht(DHTPIN, DHTTYPE);

const unsigned long INTERVALO_LECTURA_MS = 5000;   // cada cuánto se lee y envía una lectura
const unsigned long INTERVALO_ESTADO_MS  = 3000;   // cada cuánto se consulta si hay alerta activa

unsigned long ultimaLectura = 0;
unsigned long ultimoEstado  = 0;

void conectarWiFi() {
  Serial.print("Conectando a WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Conectado. IP local: ");
  Serial.println(WiFi.localIP());
}

void enviarLectura(float temperatura, float humedad) {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(String(SERVER_URL) + "/lecturas");
  http.addHeader("Content-Type", "application/json");

  String payload = "{\"temperatura\":" + String(temperatura, 1) +
                    ",\"humedad\":" + String(humedad, 1) + "}";

  int codigo = http.POST(payload);
  if (codigo > 0) {
    Serial.println("Lectura enviada (" + String(codigo) + "): " + payload);
  } else {
    Serial.println("Error al enviar lectura: " + http.errorToString(codigo));
  }
  http.end();
}

bool consultarAlerta() {
  if (WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  http.begin(String(SERVER_URL) + "/estado");
  int codigo = http.GET();
  bool activa = false;

  if (codigo == 200) {
    String respuesta = http.getString();
    activa = respuesta.indexOf("\"alerta\":true") != -1;
  } else if (codigo > 0) {
    Serial.println("El servidor respondió con código: " + String(codigo));
  } else {
    Serial.println("Error al consultar estado: " + http.errorToString(codigo));
  }
  http.end();
  return activa;
}

void setup() {
  Serial.begin(115200);

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  dht.begin();
  conectarWiFi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    conectarWiFi();
  }

  unsigned long ahora = millis();

  if (ahora - ultimaLectura >= INTERVALO_LECTURA_MS) {
    ultimaLectura = ahora;

    float humedad = dht.readHumidity();
    float temperatura = dht.readTemperature();

    if (isnan(humedad) || isnan(temperatura)) {
      Serial.println("No se pudo leer el DHT11 (revisa el cableado).");
    } else {
      Serial.println("Temp: " + String(temperatura) + " C   Humedad: " + String(humedad) + " %");
      enviarLectura(temperatura, humedad);
    }
  }

  if (ahora - ultimoEstado >= INTERVALO_ESTADO_MS) {
    ultimoEstado = ahora;
    bool alerta = consultarAlerta();
    digitalWrite(RELAY_PIN, alerta ? HIGH : LOW);
  }
}
