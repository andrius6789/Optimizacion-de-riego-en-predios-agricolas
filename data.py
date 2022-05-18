import csv
import os
from gurobipy import GRB, Model, quicksum

I_ = 2
T = 24
H = 2
D = 135
J = 3

#instanciar moddelo
model = Model()

# conjuntos

i_ = range(1, I_ + 1)
t_ = range(1, T + 1)
h_ = range(1, H + 1)
d_ = range(1, D + 1)
j_ = range(1, J + 1)

# parámetros (todos como diccionarios)

Ne = {(i, h, d): 0 for i in i_ for h in h_ for d in d_}
# se plantan ambos cultivos el primer dia y despues de esto nada mas
Ne.update({(1, 1, 1): 1})
Ne.update({(2, 2, 1): 1})

A = {1: 10000, 2: 10000} # 2 cuadrantes, ambos de 10.000 m2

DA = {d: 864000 for d in d_} # derechos de agua para cada dia d

with open(os.path.join('Data', 'Datos_resumidos.csv'), mode='r') as file:
    reader = csv.reader(file, delimiter=';')
    next(reader, None)
    next(reader, None) # saltarse headers
    Pp = {int(row[2]):float(row[3]) for row in reader} # Pp de cada dia en mm leido del csv del excel con los datos.
    ETo = {int(row[5]):float(row[6]) for row in reader} # Eto de cada dia en mm leido del csv del excel con los datos.

P = 80000000 # dato arbitrario elegido en informe E2

E = {1: 0.8, 2: 0.7, 3: 0.2}

V = {(i, j): 1 for i in i_ for j in j_}

C = {(h, t): 0.11 for h in h_ for t in t_} # clp

M = {(1, 1): 4750, (2, 1): 4750, (1, 2): 3250, (2, 2): 3250, (1, 3): 1750, (2, 3): 1750} # clp

Ce = 100000 # en L

alpha = 50000 # en L

# tiempos en dias
T1 = {1: 20, 2: 30}

T2 = {1: 20, 2: 40}

T3 = {1: 15, 2: 40}

T4 = {1: 10, 2: 25}

Tt = {1: 75, 2: 135}

Kc1 = {1: 0.7, 2:0.6}

Kc2 = {1: 1, 2: 1.15}

Kc3 =  {1: 0.95, 2: 0.8}

# variables

Z = model.addVars(h_, t_, d_, j_, vtype = GRB.CONTINUOUS, name='Z_htdj')

X = model.addVars(h_, t_, d_, vtype = GRB.CONTINUOUS, name='X_htd')

Y = model.addVars(t_, d_, vtype = GRB.CONTINUOUS, name='Y_td')

Zr = model.addVars(h_, t_, d_, vtype = GRB.CONTINUOUS, name='Zr_htd')

W = model.addVars(h_, j_, i_, vtype = GRB.BINARY, name='W_hji')

I = model.addVars(t_, d_, vtype = GRB.CONTINUOUS, name='I_td')

# restricciones

model.addConstrs(((II[t-1,d]) + sum(X[h,t,d] for h in h_) + Y[t,d] == quicksum(Z[h,t,d,j] + II[t,d] for j in j_ for h in h_) + II[t,d]) for t in range (2,T+1) for d in d_ )
# REVISAR QUE ESTE BIEN

