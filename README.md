# Monitor Inteligente de Temperatura

Proyecto de nivel básico: un ESP32 con un sensor DHT11 reporta temperatura y
humedad a un servidor. Un archivo de reglas, escrito en un mini-lenguaje
propio ("si temperatura > 28 entonces notificar"), define cuándo algo es
anormal. Un parser lee esas reglas, un motor lógico las evalúa contra cada
lectura nueva, y un dashboard en vivo muestra todo en tiempo real. Un relé
conectado al ESP32 se activa físicamente mientras haya una alerta.

La metodología completa (fases, tablero Kanban, pruebas) está en
[`docs/metodologia.md`](docs/metodologia.md).

## Arquitectura

```
ESP32 + DHT11 --WiFi/HTTP--> Servidor Flask --lee-- reglas.txt
                                    |                   |
                                    |               Parser
                                    |                   |
                                    +----------- Motor de reglas
                                    |                   |
                              Dashboard 2D          Alertas
                                    |
                          ESP32 consulta /estado --> activa relé
```

## Estructura del repositorio

```
.
├── README.md
├── .gitignore
├── docs/
│   └── metodologia.md
├── firmware/
│   └── esp32_monitor/
│       ├── esp32_monitor.ino
│       └── config.h.example      
├── servidor/
│   ├── app.py                    # servidor Flask (endpoints)
│   ├── parser.py                 # interpreta reglas.txt
│   ├── motor_reglas.py           # evalúa las reglas contra cada lectura
│   ├── reglas.txt                # reglas de ejemplo, válidas
│   └── requirements.txt
├── dashboard/
│   └── index.html                # vista en vivo (abrir directo en el navegador)
└── tests/
    └── reglas_invalidas_ejemplo.txt   # para probar que el parser no truena
```

## Hardware y conexiones

| Componente          | Pin del ESP32 | Notas                                              |
|---------------------|---------------|-----------------------------------------------------|
| DHT11 (datos)        | GPIO 4        | con resistencia pull-up entre datos y VCC            |
| DHT11 (VCC / GND)    | 3V3 / GND     |                                                       |
| Relé (IN)            | GPIO 26       | se activa mientras haya una alerta activa            |
| Relé (VCC / GND)     | según módulo  | la mayoría de módulos de un relé aceptan 5V o 3V3    |

Si tu armado usa otros pines, solo cambia `DHTPIN` y `RELAY_PIN` al inicio de
`esp32_monitor.ino`.

## Cómo correrlo

### 1. Servidor

```bash
cd servidor
pip install -r requirements.txt
python app.py
```

Queda escuchando en `http://<IP-de-tu-compu>:5000`. Anota esa IP (en la misma
red WiFi que el ESP32) — la vas a necesitar en el paso 2.

### 2. Firmware del ESP32

1. Abre `firmware/esp32_monitor/esp32_monitor.ino` en el Arduino IDE.
2. Instala las librerías **"DHT sensor library"** y **"Adafruit Unified Sensor"**
   desde el Administrador de Librerías.
3. Copia `config.h.example` a `config.h` (misma carpeta) y rellena tu WiFi y
   la IP del servidor del paso 1.
4. Compila y sube el sketch a la placa.
5. Abre el Monitor Serie (115200 baudios) para confirmar que conecta y envía
   lecturas.

### 3. Dashboard

Abre `dashboard/index.html` directamente en tu navegador (doble clic basta).
Si el servidor no corre en `localhost`, cambia la constante `SERVER_URL` al
inicio del `<script>` del archivo por la IP real del servidor.

## Probar el parser por separado

```bash
cd servidor
python parser.py ../tests/reglas_invalidas_ejemplo.txt
```

Vas a ver en consola qué líneas se aceptaron y cuáles se reportaron como
inválidas — así se prueba la Fase 4 de la metodología sin necesitar el
hardware conectado.

