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
    Pp = {int(row[2]):float(row[3].replace(',', '.')) for row in reader} # Pp de cada dia en mm leido del csv del excel con los datos.
    ETo = {int(row[5]):float(row[6].replace(',', '.')) for row in reader} # Eto de cada dia en mm leido del csv del excel con los datos.

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

Zr = model.addVars(h_, t_, d_, vtype = GRB.CONTINUOUS, name='Zr_htdj')

W = model.addVars(h_, j_, i_, vtype = GRB.BINARY, name='W_hji')

I = model.addVars(t_, d_, vtype = GRB.CONTINUOUS, name='I_td')


model.update()

# restricciones

# i
model.addConstrs(((I[t - 1, d]) + Y[t, d] == quicksum(Z[h, t, d, j] + I[t, d] for j in j_ for h in h_) for t in range(2, T + 1) for d in d_), name='R1')

model.addConstrs((I[1, d] == I[24, d - 1] for d in range(2, D + 1)), name='R2')

model.addConstr((I[1, 1] == alpha), name='R3')

# ii

model.addConstrs((quicksum(Z[h, t, d, j] * E[j] for t in t_ for j in j_) + Pp[d] * A[h] >= quicksum(Zr[h, t, d] for t in t_) for h in h_ for d in d_), name='R4')

# iii
########## faltan los indices de M
model.addConstrs((quicksum(Zr[h, t, d] for d in range(q + 1, q + T1[i] + 1) for t in t_) >= quicksum(Kc1[i] * ETo[q] - M * (1 - Ne[i, h, q]) for d in range(q + 1, q + T1[i] + 1)) for i in i_ for j in j_ for h in h_ for q in range(1, D - Tt[i] + 1)), name='R5')

model.addConstrs((quicksum(Zr[h, t, d] for d in range(q + T1[i] + 1, q + T1[i] + T2[i] + 1) for t in t_) >= quicksum((((Kc1[i] + Kc2[i]) * ETo[q]) / 2) - M * (1 - Ne[i, h, q]) for d in range(q + T1[i] + 1, q + T1[i] + T2[i] + 1)) for j in j_ for h in h_ for q in range(1, D - Tt[i] + 1) for i in i_ ), name='R6')

model.addConstrs((quicksum(Zr[h, t, d] for d in range(q + T1[i] + T2[i] + 1, q + T1[i] + T2[i] + T3[i] + 1) for t in t_) >= quicksum(((Kc2[i] * ETo[q]) / 2) - M * (1 - Ne[i, h, q]) for d in range(q + T1[i] + T2[i] + 1, q + T1[i] + T2[i] + T3[i] + 1)) for j in j_ for h in h_ for q in range(1, D - Tt[i] + 1) for i in i_ ), name='R7')

model.addConstrs((quicksum(Zr[h, t, d] for d in range(q + T1[i] + T2[i] + T3[i] + 1, q + Tt[i] + 1) for t in t_) >= quicksum((((Kc2[i] + Kc3[i]) * ETo[q]) / 2) - M * (1 - Ne[i, h, q]) for d in range(q + T1[i] + T2[i] + T3[i] + 1, q + Tt[i] + 1)) for j in j_ for h in h_ for q in range(1, D - Tt[i] + 1) for i in i_ ), name='R8')

# iv

model.addConstr((P >= quicksum(Z[h, t, d, j] * C[h, t] for j in j_ for d in d_ for t in t_ for h in h_) + quicksum(W[h, j] * A[h] * M[h, j] for j in j_ for h in h_)), name='R9')
# ************************* falta indice i en W
# v

model.addConstrs((quicksum(W[h, j, i] for j in j_) == 1 for  h in h_), name='R10')
# *************** falta indice i en W y definir i
model.addConstrs((M * W[h, j, i] >= quicksum(Z[h, t, d, j] for d in d_ for t in t_) for h in h_ for j in j_), name='R11')
################## falta definir i e indices de M

model.addConstrs((V[i, j] >= W[h, j, i] for h in h_ for j in j_ for i in i_), name='R12')

# vi

model.addConstrs((quicksum(X[h, t, d] + Y[t, d] for t in t_ for h in h_) <= DA[d] for d in d_), name='R13')

# vii

model.addConstrs((I[t, d] <= Ce for d in d_ for t in t_), name='R14')

# Naturaleza de las variables: se hace sola al instanciar las variables

# funcion objetivo

model.setObjective(quicksum(Z[h, t, d, j] for d in d_ for t in t_ for h in h_ for j in j_), GRB.MINIMIZE)

# Optimiza tu problema

model.optimize()

vo = model.ObjVal

# print("\n"+"-"*10+" Manejo Soluciones "+"-"*10)
# print(f'Valor optimo: {vo}')
# for sitio in Sitios:
#   if x[sitio].x != 0:
#     print(f'se construye campanentio en sitio {sitio}')
#   if s[sitio].x != 0:
#     print(f'se asignan {s[sitio].x} personas para vacunarse en sitio {sitio}')
#     for localidad in Localidades:
#       if y[localidad, sitio].x != 0:
#         print(f'se asocia localidad {localidad} con campamento en sitio {sitio}')
# # ¿Cuál de las restricciones son activas?
# print("\n"+"-"*9+" Restricciones Activas "+"-"*9)

# for constr in model.getConstrs():
#   print(constr, constr.getAttr('slack'))


