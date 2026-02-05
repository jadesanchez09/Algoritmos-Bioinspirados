import random # Importa la librería random para operaciones aleatorias

costos = [ # Matriz de costos entre ciudades
    [0, 5, 9, 8],
    [5, 0, 7, 6],
    [9, 7, 0, 4],
    [8, 6, 4, 0]
]

num_ciudades = len(costos) # Número de ciudades basado en la matriz de costos
#Funcion obetivo
def calcular_costo(ruta): 
    costo = 0 
    for i in range(len(ruta) - 1): 
        costo += costos[ruta[i]][ruta[i+1]] 
    costo += costos[ruta[-1]][ruta[0]]
    return costo
#Crear poblacion inicial
def crear_poblacion(tamaño):
    poblacion = []
    for _ in range(tamaño):
        ruta = list(range(num_ciudades))
        random.shuffle(ruta)
        poblacion.append(ruta)
    return poblacion
#Seleccionar la mejor ruta
def seleccionar(poblacion):
    return min(poblacion, key=calcular_costo)
#Cruzar dos rutas para crear una nueva
def cruzar(padre1, padre2):
    punto = random.randint(0, num_ciudades - 1)
    hijo = padre1[:punto] + [c for c in padre2 if c not in padre1[:punto]]
    return hijo
#Mutar una ruta intercambiando dos ciudades
def mutar(ruta):
    i, j = random.sample(range(num_ciudades), 2)
    ruta[i], ruta[j] = ruta[j], ruta[i]
    return ruta
#Algoritmo genetico principal
def algoritmo_genetico(tamaño_poblacion, generaciones):
    poblacion = crear_poblacion(tamaño_poblacion)
    mejor = seleccionar(poblacion)

    for _ in range(generaciones):
        nueva_poblacion = []
        for _ in range(tamaño_poblacion):
            padre1 = seleccionar(poblacion)
            padre2 = seleccionar(poblacion)
            hijo = cruzar(padre1, padre2)
            if random.random() < 0.3:
                hijo = mutar(hijo)
            nueva_poblacion.append(hijo)
        poblacion = nueva_poblacion
        mejor = seleccionar(poblacion)

    return mejor, calcular_costo(mejor)
# Ejecutar el algoritmo genético
ruta, costo = algoritmo_genetico(10, 50)
print("Mejor ruta:", ruta)
print("Costo:", costo)
