"""
Motor lógico: evalúa las reglas ya interpretadas por el parser contra una
lectura nueva y devuelve la lista de alertas que se cumplen.

Es la única pieza "declarativa" del proyecto: las reglas son datos (una
lista de diccionarios), no código. El motor solo las recorre y compara.
"""

OPERADORES = {
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
}


def evaluar_reglas(reglas, lectura):
    """Devuelve la lista de alertas cuyas condiciones se cumplen con `lectura`.

    `lectura` es un diccionario como {"temperatura": 29.4, "humedad": 41.0}.
    """
    alertas = []

    for regla in reglas:
        valor_actual = lectura.get(regla["variable"])
        if valor_actual is None:
            continue

        comparar = OPERADORES[regla["operador"]]
        if comparar(valor_actual, regla["valor"]):
            mensaje = regla["mensaje"] or (
                f"{regla['variable']} {regla['operador']} {regla['valor']}"
            )
            alertas.append({
                "linea_regla": regla["linea"],
                "mensaje": mensaje,
                "variable": regla["variable"],
                "valor_leido": valor_actual,
            })

    return alertas
