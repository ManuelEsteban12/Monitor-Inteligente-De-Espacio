"""
Parser del mini-lenguaje de reglas del Monitor Inteligente de Espacio.

Gramática soportada (BNF simplificado):

    regla     ::= "si" condicion "entonces" accion
    condicion ::= variable operador valor
    variable  ::= "temperatura" | "humedad"
    operador  ::= ">" | "<" | ">=" | "<=" | "=="
    valor     ::= numero
    accion    ::= "notificar" | "notificar(" texto ")"

Reglas de tolerancia a errores:
    - Líneas vacías o que empiezan con "#" se ignoran (comentarios).
    - Una línea mal escrita se reporta en consola y se ignora; el sistema
      sigue funcionando con el resto de las reglas válidas.
    - No importan mayúsculas/minúsculas ni espacios extra entre tokens.
"""

import re

PATRON_REGLA = re.compile(
    r'^\s*si\s+'
    r'(?P<variable>temperatura|humedad)\s*'
    r'(?P<operador>>=|<=|==|>|<)\s*'
    r'(?P<valor>-?\d+(\.\d+)?)\s+'
    r'entonces\s+notificar'
    r'(\s*\(\s*(?P<mensaje>"[^"]*")\s*\))?'
    r'\s*$',
    re.IGNORECASE,
)


def parsear_reglas(ruta_archivo):
    """Lee un archivo de reglas y devuelve (reglas_validas, errores).

    Cada regla válida es un diccionario:
        {"variable", "operador", "valor", "mensaje", "linea"}
    Cada error es un string listo para mostrar/loguear.
    """
    reglas = []
    errores = []

    with open(ruta_archivo, encoding="utf-8") as archivo:
        for numero_linea, linea_cruda in enumerate(archivo, start=1):
            linea = linea_cruda.strip()

            if not linea or linea.startswith("#"):
                continue

            coincidencia = PATRON_REGLA.match(linea)
            if not coincidencia:
                errores.append(f"Línea {numero_linea}: regla mal escrita -> {linea!r}")
                continue

            datos = coincidencia.groupdict()
            mensaje = datos["mensaje"].strip('"') if datos["mensaje"] else None

            reglas.append({
                "variable": datos["variable"].lower(),
                "operador": datos["operador"],
                "valor": float(datos["valor"]),
                "mensaje": mensaje,
                "linea": numero_linea,
            })

    for error in errores:
        print(f"[parser] {error}")

    return reglas, errores


if __name__ == "__main__":
    # Prueba rápida: python parser.py reglas.txt
    import sys
    ruta = sys.argv[1] if len(sys.argv) > 1 else "reglas.txt"
    reglas_validas, errores = parsear_reglas(ruta)
    print(f"\n{len(reglas_validas)} regla(s) válida(s), {len(errores)} error(es).")
    for r in reglas_validas:
        print(" ", r)
