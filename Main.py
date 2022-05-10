from re import M
from gurobipy import * #se importa todo de la biblioteca

m = Model('riego en predios agricolas') #creacion del modelo con un nombre y "m" es el objeto de la clase modelo
print(type(m))

