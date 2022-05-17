import csv
import os

I = 2
T = 24
H = 2
D = 135
J = 3

i_ = range(1, I + 1)
t_ = range(1, T + 1)
h_ = range(1, H + 1)
d_ = range(1, D + 1)
j_ = range(1, J + 1)

Ne = {(i, h, d): 0 for i in i_ for h in h_ for d in d_}
# se plantan ambos cultivos el primer dia y despues de esto nada mas
Ne.update({(1, 1, 1): 1})
Ne.update({(2, 2, 1): 1})

A = {1: 10000, 2: 10000} # 2 cuadrantes, ambos de 10.000 m2

DA = {d: 864000 for d in d_} # derechos de agua para cada dia d

f = open('Data/Datos_resumidos.csv', 'r')
f.close()

with open(os.path.join('Data', 'Datos_resumidos.csv'), mode='r') as file:
    reader = csv.reader(file)
    print(reader)
    # mydict = {rows[0]:rows[1] for rows in reader}