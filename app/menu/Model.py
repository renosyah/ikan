import numpy as np

# ini adalah fungsi neural network
# fungsi standar yang digunakan
# untuk neural network
def neural_network(nn_params, input_layer_size, hidden_layer_size, num_labels, X, y, lamb):
    
    # Untuk setiap label antara 0, 1 dan 2, akan ada vektor dengan panjang 3
    y_label_size = 3

    # Distribusi Berat dibagi menjad ke Theta1, Theta2
    Theta1 = np.reshape(nn_params[:hidden_layer_size * (input_layer_size + 1)],
                        (hidden_layer_size, input_layer_size + 1))
    Theta2 = np.reshape(nn_params[hidden_layer_size * (input_layer_size + 1):],
                        (num_labels, hidden_layer_size + 1))
 
    # Forward propagation
    m = X.shape[0]
    one_matrix = np.ones((m, 1))
    
    # Menambahkan unit bias ke layer pertama
    X = np.append(one_matrix, X, axis=1)
    a1 = X
    z2 = np.dot(X, Theta1.transpose())
    
    # Aktivasi untuk layer kedua
    a2 = 1 / (1 + np.exp(-z2))  
    one_matrix = np.ones((m, 1))
    
    # Menambahkan unit bias ke hidden layer
    a2 = np.append(one_matrix, a2, axis=1)  
    z3 = np.dot(a2, Theta2.transpose())
    
    # Aktivasi untuk layer ketiga
    a3 = 1 / (1 + np.exp(-z3))  
 
    # Mengubah label y menjadi vektor nilai boolean
    y_vect = np.zeros((m, y_label_size))
    for i in range(m):
        y_vect[i, int(y[i])] = 1
 
    # Menghitung fungsi cost
    J = (1 / m) * (np.sum(np.sum(-y_vect * np.log(a3) - (1 - y_vect) * np.log(1 - a3)))) + (lamb / (2 * m)) * (
                sum(sum(pow(Theta1[:, 1:], 2))) + sum(sum(pow(Theta2[:, 1:], 2))))
 
    # back propagation
    Delta3 = a3 - y_vect
    Delta2 = np.dot(Delta3, Theta2) * a2 * (1 - a2)
    Delta2 = Delta2[:, 1:]
 
    # gradient
    Theta1[:, 0] = 0
    Theta1_grad = (1 / m) * np.dot(Delta2.transpose(), a1) + (lamb / m) * Theta1
    Theta2[:, 0] = 0
    Theta2_grad = (1 / m) * np.dot(Delta3.transpose(), a2) + (lamb / m) * Theta2
    grad = np.concatenate((Theta1_grad.flatten(), Theta2_grad.flatten()))
 
    return J, grad