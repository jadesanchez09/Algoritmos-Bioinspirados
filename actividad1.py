import random

# -----------------------------
# FUNCIÓN OBJETIVO
# -----------------------------
# Calcula el costo total de una ruta
def costo_ruta(ruta):
    return sum(ruta)

# FUNCIÓN FITNESS
# Como queremos minimizar el costo,
# usamos el inverso para maximizar fitness
def fitness(ruta):
    return 1 / costo_ruta(ruta)

# -----------------------------
# CREAR UNA RUTA ALEATORIA
# Cada número representa el costo de un tramo
# -----------------------------
def crear_ruta():
    return [random.randint(10, 100) for _ in range(3)]

# -----------------------------
# GENERAR POBLACIÓN INICIAL
# -----------------------------
poblacion = []
for _ in range(10):
    poblacion.append(crear_ruta())

# -----------------------------
# ALGORITMO GENÉTICO
# -----------------------------
for generacion in range(20):

    # Ordenar población por fitness (mejor primero)
    poblacion.sort(key=fitness, reverse=True)

    # Mejor solución de la generación
    mejor_ruta = poblacion[0]

    print("Generación:", generacion)
    print("Mejor ruta:", mejor_ruta)
    print("Costo total:", costo_ruta(mejor_ruta))
    print("---------------------------")

    # SELECCIÓN: tomar las mejores rutas
    padres = poblacion[:5]

    # CRUZA: generar nueva población
    nueva_poblacion = padres.copy()

    while len(nueva_poblacion) < 10:
        padre1, padre2 = random.sample(padres, 2)

        # Cruza simple
        hijo = [padre1[0], padre2[1], padre1[2]]
        nueva_poblacion.append(hijo)

    poblacion = nueva_poblacion
