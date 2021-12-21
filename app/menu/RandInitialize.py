import numpy as np

# fungsi random initializer
# adalah fungsi untuk melakukan inisialisasi
# random dan ini adalah fungsi standar
def initialise(a, b):
    epsilon = 0.15
    c = np.random.rand(a, b + 1) * ( 2 * epsilon) - epsilon 
    return c