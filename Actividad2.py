import random # Importa la librería random para operaciones aleatorias

costos = [ #I changed the cost matrix to have 5 cities instead of 4 
                                #and I added some random costs between them.
    [15, 29, 59, 18, 17],
    [84, 11, 7, 2, 4],
    [19, 12, 20, 4, 3],
    [28, 86, 7, 32, 2],
    [17, 4, 23, 2, 8]
]

num_ciudades = len(costos) # Número de ciudades basado en la matriz de costos


#Funcion objetivo with a penalty 
def calcular_costo(ruta):
    costo = 0
    
    for i in range(len(ruta)-1):
        costo += costos[ruta[i]][ruta[i+1]]

    costo += costos[ruta[-1]][ruta[0]]

    # Apply penalty if cost exceeds threshold
    if costo > 100:
        costo += 50

    return costo


#Crear poblacion inicial
def crear_poblacion(tamaño):
    poblacion = []
    for _ in range(tamaño):
        ruta = list(range(num_ciudades))
        random.shuffle(ruta)
        poblacion.append(ruta)
    return poblacion

#here we change the selection method 
def seleccionar(poblacion, k=3): #k3 means that we are going to select the best solution among 3 random candidates from the population, this is a common selection method called tournament selection
    candidatos = random.sample(poblacion, k)
    return min(candidatos, key=calcular_costo)

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


# Algoritmo genético principal
def algoritmo_genetico(tamaño_poblacion, generaciones):
    poblacion = crear_poblacion(tamaño_poblacion)
    mejor = seleccionar(poblacion)

    for _ in range(generaciones):
        nueva_poblacion = []
        for _ in range(tamaño_poblacion):
            padre1 = seleccionar(poblacion)
            padre2 = seleccionar(poblacion)
            hijo = cruzar(padre1, padre2)
            if random.random() < 0.7: #Here we increase the mutation rate to 70% to encourage more exploration of the solution space
                hijo = mutar(hijo)
            nueva_poblacion.append(hijo)
        poblacion = nueva_poblacion
        mejor = seleccionar(poblacion)

    # here we return not only the best route and its cost
    # but also the final population of routes, so we can analyze them later if we want
    return mejor, calcular_costo(mejor), poblacion

# execute
ruta, costo, poblacion_final = algoritmo_genetico(100, 1200) # we increase the population size to 100 
                                                                #and the number of generations to 1200 to give the algorithm more chances to find a good solution

# Mostrar la mejor ruta
print("Mejor ruta:", ruta) #here we print the best route found 
print("Costo:", costo)
