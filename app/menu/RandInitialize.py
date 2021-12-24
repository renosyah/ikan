import numpy as np

# fungsi random initializer
# adalah fungsi untuk melakukan inisialisasi
# random dan ini adalah fungsi standar
def initialise(a, b):
    epsilon = 0.15
    
     # Secara acak menginisialisasi nilai thetas antara [-epsilon, +epsilon]
    c = np.random.rand(a, b + 1) * ( 2 * epsilon) - epsilon 
    
    return c