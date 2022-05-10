from gurobipy import * #se importa todo de la biblioteca
from gurobipy import GRB
#m.write("riego en predios agricolas.lp")

m = Model('riego en predios agricolas') #creacion del modelo con un nombre y "m" es el objeto de la clase modelo

#valores limites de los conjuntos. SUJETOS A CAMBIOS -> '' hacerlos input ''
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

#conjuntos/parametros
Ne = [{i,h,d} for i in i_ for h in h_ for d in d_] #hay que darle valor 1 o 0
A = [{h} for h in h_] #como le asociamos valores reales de m^2 a cada area para todo h?, son valores iguales para todo h?
DA = [{d} for d in d_] #misma pregunta re arriba, es un valor constante no? podria quedar DA = input("cuales son sus derechos de agua en metros cubicos")
ETo = [{d} for d in d_]
P = input("cual es su presupuesto en pesos?: ") #para todos los dias d
E = [{j,t} for j in j_ for t in t_] #como asociar valores no randomizados a cada par de puntos? quizas son valores entonces habria que especificar la eficiencia por hora
PP = [{d} for d in d_] #como ingresan estos valores al programa?
V = [{i,j} for i in i_ for j in j_] #hacer binario. Se me ocurre que se podria tratar como variable y crear como GRB.BINARY
C = [{h,t} for h in h_ for t in t_]
M = [{h,j} for h in h_ for j in j_]
Ce = input('Cual es la capacidad del estanque en Litros: ')
alfa = input('agua almacenada al inicio, en Litros: ')
T1 = [{i} for i in i_]
T2 = [{i} for i in i_]
T3 = [{i} for i in i_]
T4 = [{i} for i in i_]
Tt = [T1 + T2 + T3 + T4 for i in i_] #revisar que este bien definido
#print(type(T1[0]))
Kc1 = [{i} for i in i_]
Kc2 = [{i} for i in i_]
Kc3 = [{i} for i in i_]

Z = m.addVars(h_,t_,d_,j_)
X = m.addVars(h_,t_,d_)
Y = m.addVars(t_,d_)
Zr =m.addVars(h_,t_,d_)
W = m.addVars(h_,j_,i_, vtype= GRB.BINARY)
II =m.addVars(t_,d_) #Este es I pero ya existe un valor I para los rangos

#Restriccion i) 
## Como agregas una igualdad de valores para un punto del conjunto especifico??
###dice como comentario que sobra X, habria que eliminar la suma de Xhtd y listo considerando que se soluciona "##"
m.addConstrs(((II[t-1,d]) + sum(X[h,t,d] for h in h_) + Y[t,d] == quicksum(Z[h,t,d,j] + II[t,d] for j in j_ for h in h_) + II[t,d]) for t in range (2,T+1) for d in d_ )

#Restriccion ii)
#m.addConstrs(quicksum(Z[h,t,d,j]*E[j,t] for t in t_ for j in j_) + Pp[d] * A[h] >= sum(Zr[h,t,d]) for h in h_ for d in d_)
#la naturaleza de algun valor esta definido como tuplas (puntos) y no como valores por lo que no genera una restriccion valida

#Restriccion iii)
# :O

#Restriccion iv)
# m.addConstrs(P >= quicksum(C[h,t] for j in j_ for d in d_ for t in t_ for h in h_) + quicksum(W[h,j] * M[h,j] for j in j_ for h in h_))
#lo mismo de ii)
## me parece que esta bien definida, el problema es la manera en las que estan construidos los parametros

#Restriccion v)

#m.addConstrs( sum(W[j,h] for j in j_) == 1 for h in h_ )
#parece que lo mismo de ii y iv

#m.addConstrs(M * W[h,j,i] >= quicksum(Z[h,t,d,j] for d in d_ for t in t_) for h in h_ for j in j_ for i in i_)
#agregue el para todo i de i_ porque no estaba considerado

#m.addConstrs( V[i,j] >= W[h,j,i] for h in h_ for j in j_ for i in i_)
#hay que definir bien las cosas, siguen siendo tuplas

#Restriccion vi)

#m.addConstrs( quicksum(X[h,t,d] + Y[t,d] for t in t_ for h in h_) <= DA[d] for d in d_)
##corregir naturaleza 

#Restriccion vii)
#m.addConstrs( II[t,d] <= C[e] for d in d_ for t in t_) cual es el rango de e???

funcion_objetivo = quicksum(Z[h,t,d,j] for d in d_ for t in t_ for h in h_ for j in j_)
m.setObjetive(funcion_objetivo, GRB.MINIMIZE)

