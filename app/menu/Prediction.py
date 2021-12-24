import numpy as np

# ini adalah fungsi prediksi
# dimana input akan di hitung dan diprediksi
# menggunakan training model yang telah dibuat sebelumnya
# ini adalah fungsi standar
def predict(Theta1, Theta2, X):
    m = X.shape[0]
    
    # Aktivasi untuk layer pertama
    one_matrix = np.ones((m, 1))
    
    # Menambahkan unit bias ke layer pertama
    X = np.append(one_matrix, X, axis=1) 
    z2 = np.dot(X, Theta1.transpose())
    
    # Aktivasi untuk layer kedua
    a2 = 1 / (1 + np.exp(-z2))  
    one_matrix = np.ones((m, 1))
    
    # Menambahkan unit bias ke hidden layer
    a2 = np.append(one_matrix, a2, axis=1)  
    z3 = np.dot(a2, Theta2.transpose())
    
    # Aktivasi untuk layer ketiga
    a3 = 1 / (1 + np.exp(-z3))  
    
     # Memprediksi kelas berdasarkan nilai maksimal hipotesis
    p = (np.argmax(a3, axis=1))
    
    return p, a3[0]