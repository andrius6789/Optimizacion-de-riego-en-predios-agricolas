from re import M
from gurobipy import * #se importa todo de la biblioteca

m = Model('riego en predios agricolas') #creacion del modelo con un nombre y "m" es el objeto de la clase modelo
print(type(m))

#valores limites de los conjuntos. SUJETOS A CAMBIOS
D = 28
I = 5
H = 100
T = 24 #no cambiar este
J = 3

#rangos
d_ = range(1, D + 1) #dias
i_ = range(1, I + 1) #tipo de cultivo
h_ = range(1, H + 1) #cuadrante
t_ = range(1, T + 1) #horas
j_ = range(1, J + 1) #metodos de riego

#conjuntos
    
