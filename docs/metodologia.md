# Metodología del proyecto — Monitor Inteligente de Espacio (Nivel Básico)

> Nota: la presentación final del proyecto usa un enfoque **Kanban** (tablero
> por hacer / en progreso / hecho) para organizar el trabajo día a día. Este
> documento describe las fases de fondo que hay detrás de ese tablero —
> qué se define antes de programar, qué cubre cada tarjeta del Kanban, y
> cómo se valida el sistema al final.

## 1. Enfoque general

El proyecto tiene dos naturalezas distintas al mismo tiempo. Por un lado hay
una parte de **hardware/firmware** (ESP32 + DHT11 + relé), que necesita
definirse casi por completo antes de poder avanzar: no tiene sentido escribir
el parser si todavía no se sabe qué datos manda el sensor. Por otro lado hay
una parte de **software** (servidor, parser, motor de reglas, dashboard) que
se beneficia de construirse en tareas cortas y verificables, cada una movida
por el tablero Kanban de "por hacer" a "en progreso" a "hecho".

## 2. Fases

### Fase 0 — Definición y alcance

Objetivo: dejar por escrito qué hace el sistema y qué no, antes de tocar código.

- Variable a monitorear: temperatura y humedad, leídas con un sensor DHT11.
- Frecuencia de muestreo: cada 5 segundos (ajustable en el firmware).
- Formato de los datos que viajan del ESP32 al servidor: JSON vía HTTP POST.
- Ejemplos de reglas de alerta: "si temperatura > 28 entonces notificar",
  "si humedad < 30 entonces notificar('aire muy seco')".

### Fase 1 — Arquitectura

```
[ESP32 + DHT11] --(WiFi, HTTP POST /lecturas)--> [Servidor Flask]
                                                        |
                                              [Archivo de reglas .txt]
                                                        |
                                                  [Parser] --produce--> [Reglas evaluables]
                                                        |
                                                  [Motor lógico] --evalúa--> [Alertas]
                                                        |
                        [Dashboard 2D] <--GET /lecturas y /alertas--
                                                        |
                        [ESP32] <--GET /estado (activa el relé)--
```

El relé es la única diferencia respecto al diseño original: además de avisar
en el dashboard, el propio ESP32 consulta `/estado` cada pocos segundos y
enciende físicamente el relé mientras haya una alerta activa.

### Fase 2 — Diseño del mini-lenguaje de reglas

Gramática (BNF simplificado):

```
regla       ::= "si" condicion "entonces" accion
condicion   ::= variable operador valor
variable    ::= "temperatura" | "humedad"
operador    ::= ">" | "<" | ">=" | "<=" | "=="
valor       ::= numero
accion      ::= "notificar" | "notificar(" texto ")"
```

El parser tolera números decimales, espacios extra y mayúsculas/minúsculas.
Una línea mal escrita se reporta en consola y se ignora, sin detener el
resto del sistema (ver `tests/reglas_invalidas_ejemplo.txt`).

### Fase 3 — Desarrollo (tablero Kanban)

Las tareas del tablero, en el orden en que normalmente se mueven de
"por hacer" a "hecho":

1. **Firmware y sensores** — el ESP32 lee el DHT11 y envía datos reales por WiFi.
2. **Servidor** — recibe y guarda las lecturas, expone los endpoints de consulta.
3. **Parser + motor de reglas** — interpreta `reglas.txt` y evalúa alertas.
4. **Dashboard + integración** — vista en vivo conectada de punta a punta,
   incluyendo el relé reaccionando a las alertas.

A diferencia de un cronograma por sprints con fechas fijas, en Kanban cada
tarjeta avanza en cuanto la anterior está lista, y se limita cuántas tarjetas
están "en progreso" a la vez para no dispersar el esfuerzo.

### Fase 4 — Pruebas y validación

- Reglas inválidas: confirmar que el error se reporta sin detener el sistema
  (usar `tests/reglas_invalidas_ejemplo.txt`).
- Alertas reales: provocar manualmente una condición (acercar calor al DHT11)
  y verla aparecer en el dashboard y activar el relé.
- Latencia: medir cuánto tarda una lectura en llegar del ESP32 al dashboard.
- Estabilidad: dejar el sistema corriendo 30-60 minutos y revisar caídas o
  pérdidas de datos.

### Fase 5 — Documentación y cierre

- Arquitectura final (con los cambios respecto al diseño inicial, si los hubo).
- Gramática final del mini-lenguaje de reglas.
- Instrucciones para levantar el sistema desde cero (ver `README.md`).
- Presentación del proyecto para mostrarlo.
