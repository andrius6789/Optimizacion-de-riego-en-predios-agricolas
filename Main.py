import csv
import os
from gurobipy import GRB, Model, quicksum


# IMPORTANTE ************************************************
# ***********************************************************
# ***********************************************************
# ***********************************************************

# PARA WINDOWS, abrir con esto:
path = os.path.join("Optimizacion-de-riego-en-predios-agricolas\Data\Datos_resumidos.csv")

# PARA MAC, abrir con esto:
path = os.path.join('Data', 'Datos_resumidos.csv')

# ***********************************************************
# ***********************************************************
# ***********************************************************

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

# parametros (todos como diccionarios)

Ne = {(i, h, d): 0 for i in i_ for h in h_ for d in d_}

for d in d_:
    Ne.update({(1, 1, d): 1})
    Ne.update({(2, 2, d): 1})
    

A = {1: 10000, 2: 10000} # 2 cuadrantes, ambos de 10.000 m2

DA = {d: 864000 for d in d_} # derechos de agua para cada dia d

with open(path, mode='r') as file:
    reader = csv.reader(file, delimiter=';')
    next(reader, None)
    next(reader, None) # saltarse headers
    Pp = dict()
    ETo = dict()
    for col in reader:
        Pp.update({int(col[2]):float(col[3].replace(',', '.'))}) # Pp de cada dia en mm leido del csv del excel con los datos.
        ETo.update({int(col[5]):float(col[6].replace(',', '.'))}) # ETo de cada dia en mm leido del csv del excel con los datos.

P = 80000000 # dato arbitrario elegido en informe E2

E = {1: 0.8, 2: 0.7, 3: 0.2}

V = {(i, j): 1 for i in i_ for j in j_}

C = {(h, t): 0.11 for h in h_ for t in t_} # clp

M = {(1, 1): 4750, (2, 1): 4750, (1, 2): 3250, (2, 2): 3250, (1, 3): 1750, (2, 3): 1750} # clp

Ce = 100000 # en L
# Ce = 100000999999999999 # en L

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

Mg = 1000000000000000 # M grande

# variables

Z = model.addVars(h_, t_, d_, j_, vtype = GRB.CONTINUOUS, name='Z_htdj')

X = model.addVars(h_, t_, d_, vtype = GRB.CONTINUOUS, name='X_htd')

Y = model.addVars(t_, d_, vtype = GRB.CONTINUOUS, name='Y_td')

Zr = model.addVars(h_, t_, d_, vtype = GRB.CONTINUOUS, name='Zr_htdj')

W = model.addVars(h_, j_, i_, vtype = GRB.BINARY, name='W_hji')

I = model.addVars(t_, d_, vtype = GRB.CONTINUOUS, name='I_td')

Xe = model.addVars(h_, t_, d_, vtype = GRB.CONTINUOUS, name='Xe_htd')


model.update()

# restricciones

# i
# model.addConstrs(((I[t - 1, d]) + Y[t, d] == quicksum(Z[h, t, d, j] + I[t, d] for j in j_ for h in h_) for t in range(2, T + 1) for d in d_), name='R1')

model.addConstrs(((I[t - 1, d]) + Y[t, d]  == quicksum(Z[h, t, d, j] for j in j_ for h in h_) + I[t, d] + quicksum(Xe[h, t, d] for h in h_) for t in range(2, T + 1) for d in d_), name='R1')

model.addConstrs((I[1, d] == I[24, d - 1] for d in range(2, D + 1)), name='R2')

model.addConstr((I[1, 1] == alpha), name='R3')

# ii

model.addConstrs((quicksum(Z[h, t, d, j] * E[j] for t in t_ for j in j_) + Pp[d] * A[h] >= quicksum(Zr[h, t, d] for t in t_) for h in h_ for d in d_), name='R4')

# iii
# model.addConstrs((quicksum(Zr[h, t, d] for t in t_) >= Kc1[i] * ETo[q] * A[h] - Mg * (1 - Ne[i, h, q]) for i in i_ for j in j_ for h in h_ for q in range(1, D - Tt[i] + 1) for d in range(q, q + T1[i] + 1)), name='R5')

# model.addConstrs((quicksum(Zr[h, t, d] for t in t_) >= (((Kc1[i] + Kc2[i]) * ETo[q] * A[h]) / 2) - Mg * (1 - Ne[i, h, q]) for i in i_ for j in j_ for h in h_ for q in range(1, D - Tt[i] + 1) for d in range(q + T1[i] + 1, q + T1[i] + T2[i] + 1) ), name='R6')

# model.addConstrs((quicksum(Zr[h, t, d] for t in t_) >= ((Kc2[i] * ETo[q] * A[h]) / 2) - Mg * (1 - Ne[i, h, q]) for i in i_ for j in j_ for h in h_ for q in range(1, D - Tt[i] + 1) for d in range(q + T1[i] + T2[i] + 1, q + T1[i] + T2[i] + T3[i] + 1)), name='R7')

# model.addConstrs((quicksum(Zr[h, t, d] for t in t_) >= (((Kc2[i] + Kc3[i]) * ETo[q] * A[h]) / 2) - Mg * (1 - Ne[i, h, q]) for i in i_ for j in j_ for h in h_ for q in range(1, D - Tt[i] + 1) for d in range(q + T1[i] + T2[i] + T3[i] + 1, q + Tt[i] + 1)), name='R8')

# Las 3 restricciones de arriba deberian ser suficientes para que el modelo funcione,
# pero por alguna razon que no sabemos, no se crean las restricciones para
# h=2, por lo que para solucionarlo se añaden manualmente en las siguientes lineas:

model.addConstrs((quicksum(Zr[1, t, d] for t in t_) >= Kc1[i] * ETo[q] * A[1] - Mg * (1 - Ne[i, 1, q]) for i in i_ for j in j_ for q in range(1, D - Tt[i] + 1) for d in range(q, q + T1[i] + 1)), name='R5')

model.addConstrs((quicksum(Zr[1, t, d] for t in t_) >= (((Kc1[i] + Kc2[i]) * ETo[q] * A[1]) / 2) - Mg * (1 - Ne[i, 1, q]) for i in i_ for j in j_ for q in range(1, D - Tt[i] + 1) for d in range(q + T1[i] + 1, q + T1[i] + T2[i] + 1) ), name='R6')

model.addConstrs((quicksum(Zr[1, t, d] for t in t_) >= ((Kc2[i] * ETo[q] * A[1]) / 2) - Mg * (1 - Ne[i, 1, q]) for i in i_ for j in j_ for q in range(1, D - Tt[i] + 1) for d in range(q + T1[i] + T2[i] + 1, q + T1[i] + T2[i] + T3[i] + 1)), name='R7')

model.addConstrs((quicksum(Zr[1, t, d] for t in t_) >= (((Kc2[i] + Kc3[i]) * ETo[q] * A[1]) / 2) - Mg * (1 - Ne[i, 1, q]) for i in i_ for j in j_ for q in range(1, D - Tt[i] + 1) for d in range(q + T1[i] + T2[i] + T3[i] + 1, q + Tt[i] + 1)), name='R8')

model.addConstrs((quicksum(Zr[2, t, d] for t in t_) >= Kc1[i] * ETo[q] * A[2] - Mg * (1 - Ne[i, 1, q]) for i in i_ for j in j_ for q in range(1, D - Tt[i] + 1) for d in range(q, q + T1[i] + 1)), name='R51')

model.addConstrs((quicksum(Zr[2, t, d] for t in t_) >= (((Kc1[i] + Kc2[i]) * ETo[q] * A[2]) / 2) - Mg * (1 - Ne[i, 2, q]) for i in i_ for j in j_ for q in range(1, D - Tt[i] + 1) for d in range(q + T1[i] + 1, q + T1[i] + T2[i] + 1) ), name='R61')

model.addConstrs((quicksum(Zr[2, t, d] for t in t_) >= ((Kc2[i] * ETo[q] * A[2]) / 2) - Mg * (1 - Ne[i, 2, q]) for i in i_ for j in j_ for q in range(1, D - Tt[i] + 1) for d in range(q + T1[i] + T2[i] + 1, q + T1[i] + T2[i] + T3[i] + 1)), name='R71')

model.addConstrs((quicksum(Zr[2, t, d] for t in t_) >= (((Kc2[i] + Kc3[i]) * ETo[q] * A[2]) / 2) - Mg * (1 - Ne[i, 2, q]) for i in i_ for j in j_ for q in range(1, D - Tt[i] + 1) for d in range(q + T1[i] + T2[i] + T3[i] + 1, q + Tt[i] + 1)), name='R81')
    
# iv

model.addConstr((P >= quicksum(Z[h, t, d, j] * C[h, t] for j in j_ for d in d_ for t in t_ for h in h_) + quicksum(W[h, j, i] * A[h] * M[h, j] for j in j_ for h in h_ for i in i_)), name='R9')

# model.addConstr((P >= quicksum(X[h, t, d] * C[h, t] for d in d_ for t in t_ for h in h_) + quicksum(W[h, j, i] * A[h] * M[h, j] for j in j_ for h in h_ for i in i_)), name='R9')

# model.addConstr((P >= quicksum(Zr[h, t, d] * C[h, t] for d in d_ for t in t_ for h in h_) + quicksum(W[h, j, i] * A[h] * M[h, j] for j in j_ for h in h_ for i in i_)), name='R9')

# v

model.addConstrs((quicksum(W[h, j, i] for j in j_ for i in i_) == 1 for h in h_), name='R10')

model.addConstrs((Mg * W[h, j, i] >= quicksum(Z[h, t, d, j] * Ne[h, i, d] for d in d_ for t in t_) for h in h_ for j in j_ for i in i_), name='R11')

model.addConstrs((V[i, j] >= W[h, j, i] for h in h_ for j in j_ for i in i_), name='R12')

# vi

# model.addConstrs((quicksum(X[h, t, d] for t in t_ for h in h_) + quicksum(Y[t, d] for t in t_) <= DA[d] for d in d_), name='R13')

model.addConstrs((quicksum(X[h, t, d] + Xe[h, t, d] for t in t_ for h in h_) <= DA[d] for d in d_), name='R13')

# vii

model.addConstrs((I[t, d] <= Ce for d in d_ for t in t_), name='R14')

# viii

model.addConstrs((quicksum(Z[h,t,d,j] for j in j_) <= X[h,t,d] + Xe[h,t,d] for h in h_ for t in t_ for d in d_), name='R15')

# Naturaleza de las variables: se hace sola al instanciar las variables


# model.addConstrs((Z[h, 1, d, j] == 0 for h in h_ for d in d_ for j in j_), name='R11')

# model.addConstrs((Y[1, d] == 0 for d in d_), name='R111')

# model.addConstrs((X[h, 1, d] == 0 for h in h_ for d in d_), name='R1111')


# funcion objetivo

model.setObjective(quicksum(Z[h, t, d, j] for d in d_ for t in t_ for h in h_ for j in j_), GRB.MINIMIZE)

# Optimiza tu problema

model.optimize()

vo = model.ObjVal

print("\n"+"-"*10+" Manejo Soluciones "+"-"*10)
print(f'Valor optimo: {vo}L')
        
for h in h_:
    for j in j_:
        for i in i_:
            if W[h, j, i].x != 0:
                print(f'Cuadrante h={h} con cultivo i={i} se riega a través del método j={j}')

print(f'Costo de la solución: ${sum([Z[h, t, d, j].x * C[h, t] for j in j_ for d in d_ for t in t_ for h in h_]) + sum([W[h, j, i].x * A[h] * M[h, j] for j in j_ for h in h_ for i in i_])}')

print('Holguras')

# for t in t_:
#     for d in d_:
#         constr = model.getConstrByName(f'R1[{t},{d}]')
#         if constr:
#             slack = constr.getAttr(GRB.Attr.Slack)
#             if slack == 0:
#                 print(f'R1[{t},{d}] es activa')

# for d in d_:
#     constr = model.getConstrByName(f'R2[{d}]')
#     if constr:
#         slack = constr.getAttr(GRB.Attr.Slack)
#         if slack == 0:
#             print(f'R2[{d}] es activa')

# constr = model.getConstrByName(f'R3')
# if constr:
#     slack = constr.getAttr(GRB.Attr.Slack)
#     if slack == 0:
#         print(f'R3 es activa')

# for h in h_:
#     for d in d_:
#         constr = model.getConstrByName(f'R4[{h},{d}]')
#         if constr:
#             slack = constr.getAttr(GRB.Attr.Slack)
#             if slack == 0:
#                 print(f'R4[{h},{d}] es activa')

# for i in i_:
#     for j in j_:
#         for q in d_:
#             for d in d_:
#                 constr = model.getConstrByName(f'R5[{i},{j},{q},{d}]')
#                 if constr:
#                     slack = constr.getAttr(GRB.Attr.Slack)
#                     if slack == 0:
#                         print(f'R5[{i},{j},{q},{d}] es activa')
                        
# for i in i_:
#     for j in j_:
#         for q in d_:
#             for d in d_:
#                 constr = model.getConstrByName(f'R6[{i},{j},{q},{d}]')
#                 if constr:
#                     slack = constr.getAttr(GRB.Attr.Slack)
#                     if slack == 0:
#                         print(f'R6[{i},{j},{q},{d}] es activa')
                        
# for i in i_:
#     for j in j_:
#         for q in d_:
#             for d in d_:
#                 constr = model.getConstrByName(f'R7[{i},{j},{q},{d}]')
#                 if constr:
#                     slack = constr.getAttr(GRB.Attr.Slack)
#                     if slack == 0:
#                         print(f'R7[{i},{j},{q},{d}] es activa')

# for i in i_:
#     for j in j_:
#         for q in d_:
#             for d in d_:
#                 constr = model.getConstrByName(f'R8[{i},{j},{q},{d}]')
#                 if constr:
#                     slack = constr.getAttr(GRB.Attr.Slack)
#                     if slack == 0:
#                         print(f'R8[{i},{j},{q},{d}] es activa')

# for i in i_:
#     for j in j_:
#         for q in d_:
#             for d in d_:
#                 constr = model.getConstrByName(f'R51[{i},{j},{q},{d}]')
#                 if constr:
#                     slack = constr.getAttr(GRB.Attr.Slack)
#                     if slack == 0:
#                         print(f'R51[{i},{j},{q},{d}] es activa')

# for i in i_:
#     for j in j_:
#         for q in d_:
#             for d in d_:
#                 constr = model.getConstrByName(f'R61[{i},{j},{q},{d}]')
#                 if constr:
#                     slack = constr.getAttr(GRB.Attr.Slack)
#                     if slack == 0:
#                         print(f'R61[{i},{j},{q},{d}] es activa')

# for i in i_:
#     for j in j_:
#         for q in d_:
#             for d in d_:
#                 constr = model.getConstrByName(f'R71[{i},{j},{q},{d}]')
#                 if constr:
#                     slack = constr.getAttr(GRB.Attr.Slack)
#                     if slack == 0:
#                         print(f'R71[{i},{j},{q},{d}] es activa')

# for i in i_:
#     for j in j_:
#         for q in d_:
#             for d in d_:
#                 constr = model.getConstrByName(f'R81[{i},{j},{q},{d}]')
#                 if constr:
#                     slack = constr.getAttr(GRB.Attr.Slack)
#                     if slack == 0:
#                         print(f'R81[{i},{j},{q},{d}] es activa')

# constr = model.getConstrByName(f'R9')
# if constr:
#     slack = constr.getAttr(GRB.Attr.Slack)
#     if slack == 0:
#         print(f'R9 es activa')

# for h in h_:
#     constr = model.getConstrByName(f'R10[{h}]')
#     if constr:
#         slack = constr.getAttr(GRB.Attr.Slack)
#         if slack == 0:
#             print(f'R10[{h}] es activa')
            
# for h in h_:
#     for j in j_:
#         for i in i_:
#             constr = model.getConstrByName(f'R11[{h},{j},{i}]')
#             if constr:
#                 slack = constr.getAttr(GRB.Attr.Slack)
#                 if slack == 0:
#                     print(f'R11[{h},{j},{i}] es activa')

# for h in h_:
#     for j in j_:
#         for i in i_:
#             constr = model.getConstrByName(f'R12[{h},{j},{i}]')
#             if constr:
#                 slack = constr.getAttr(GRB.Attr.Slack)
#                 if slack == 0:
#                     print(f'R12[{h},{j},{i}] es activa')

# for d in d_:
#     constr = model.getConstrByName(f'R13[{d}]')
#     if constr:
#         slack = constr.getAttr(GRB.Attr.Slack)
#         if slack == 0:
#             print(f'R13[{d}] es activa')

# for d in d_:
#     for t in t_:
#         constr = model.getConstrByName(f'R14[{d},{t}]')
#         if constr:
#             slack = constr.getAttr(GRB.Attr.Slack)
#             if slack == 0:
#                 print(f'R14[{d},{t}] es activa')

# for h in h_:
#     for t in t_:
#         for d in d_:
#             constr = model.getConstrByName(f'R15[{h},{t},{d}]')
#             if constr:
#                 slack = constr.getAttr(GRB.Attr.Slack)
#                 if slack == 0:
#                     print(f'R15[{h},{t},{d}] es activa')



# for t in range(2, T + 1):
#     for d in d_:
#         der = sum(Z[h,t,d,j].x for j in j_ for h in h_) + I[t,d].x
#         izq = I[t - 1, d].x + Y[t,d].x + sum(X[h, t, d].x for h in h_)
#         print(f'{izq} = {der}')
            
# print('==============')
# for t in range(1, T + 1):
#     for d in d_:
#         res = sum(Z[h,t,d,j].x for j in j_ for h in h_)
#         if res>2:
#             print(f'{res}')