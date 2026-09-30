"""
Servidor del Monitor Inteligente de Espacio.

Recibe lecturas del ESP32, las guarda en memoria, las evalúa contra las
reglas del archivo reglas.txt (vía parser.py y motor_reglas.py), y expone
esa información para el dashboard y para el propio ESP32 (que consulta
/estado para saber si debe activar el relé).

Cómo correrlo:
    pip install -r requirements.txt
    python app.py

El servidor queda escuchando en el puerto 5000, en todas las interfaces
de red (0.0.0.0), para que el ESP32 pueda alcanzarlo desde la misma WiFi.
"""

from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

from motor_reglas import evaluar_reglas
from parser import parsear_reglas

RUTA_REGLAS = "reglas.txt"
MAX_LECTURAS_GUARDADAS = 200

app = Flask(__name__)
CORS(app)  # permite que el dashboard (abierto como archivo local) consulte la API

reglas, errores_parser = parsear_reglas(RUTA_REGLAS)
lecturas = []
alertas_activas = []


@app.route("/lecturas", methods=["POST"])
def recibir_lectura():
    global alertas_activas

    datos = request.get_json(force=True, silent=True)
    if not datos or "temperatura" not in datos or "humedad" not in datos:
        return jsonify({"error": "faltan los campos 'temperatura' y/o 'humedad'"}), 400

    try:
        lectura = {
            "temperatura": float(datos["temperatura"]),
            "humedad": float(datos["humedad"]),
            "hora": datetime.now().strftime("%H:%M:%S"),
        }
    except (TypeError, ValueError):
        return jsonify({"error": "'temperatura' y 'humedad' deben ser numéricos"}), 400

    lecturas.append(lectura)
    if len(lecturas) > MAX_LECTURAS_GUARDADAS:
        lecturas.pop(0)

    alertas_activas = evaluar_reglas(reglas, lectura)

    return jsonify({"ok": True, "lectura": lectura, "alertas": alertas_activas}), 201


@app.route("/lecturas", methods=["GET"])
def obtener_lecturas():
    return jsonify(lecturas)


@app.route("/alertas", methods=["GET"])
def obtener_alertas():
    return jsonify(alertas_activas)


@app.route("/estado", methods=["GET"])
def obtener_estado():
    # Endpoint que consulta el propio ESP32 para decidir si activa el relé.
    return jsonify({"alerta": len(alertas_activas) > 0})


@app.route("/reglas", methods=["GET"])
def obtener_reglas_cargadas():
    return jsonify({"reglas": reglas, "errores": errores_parser})


if __name__ == "__main__":
    if errores_parser:
        print(f"[app] {len(errores_parser)} regla(s) con error en {RUTA_REGLAS}; revisa el detalle arriba.")
    print(f"[app] {len(reglas)} regla(s) cargada(s) correctamente.")
    app.run(host="0.0.0.0", port=5000, debug=True)
