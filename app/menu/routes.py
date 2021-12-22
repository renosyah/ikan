from flask import request, render_template, send_from_directory, redirect
from . import menu
import os
from flask import jsonify
import numpy as np
import matplotlib.pyplot as plt
import cv2
import random
from .Model import neural_network
from .RandInitialize import initialise
from .Prediction import predict
from scipy.optimize import minimize

# default setting
LABEL_NAMES = ["Segar","Agak Segar","Busuk"]
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}
IMG_SIZE = 28
DATADIR = os.path.join("app","dataset")
CLASSES = ["0","1","2"]
MAX_TRAINING_EXAMPLE = 400
MAX_TRAINING_TEST = 300
Y_LABEL_SIZE = 3

# header response
# memberikan type header response
# setiap route fungsi selesai dipanggil
@menu.after_request
def add_header(response):
    response.cache_control.max_age = -1
    return response

# file serve
# router yg berfungsi menyediakan
# static file seperti js dan css
@menu.route('/<path:folder_name>/<path:filename>', methods=['GET'])
def serve_static(folder_name,filename):
    return send_from_directory(os.path.join('files',folder_name), filename)

# index routes
# fungsi route untuk menampilkan 
# halaman utama
@menu.route('/', methods=['GET'])
def index():
    return render_template('menu/index.html')

# training routes
# fungsi route untuk menampilkan
# halaman training
@menu.route('/training', methods=['GET'])
def training():
    return send_from_directory(os.path.join('templates','menu'), 'training.html')

# training routes
# fungsi route untuk menangani
# permintaan API mengecheck
# data model training
@menu.route('/training/<path:target_param>', methods=['GET','POST'])
def training_model(target_param):
    return jsonify({'is_exist': os.path.exists(os.path.join('app','training',target_param,'Theta1.csv')),'target_param' : target_param}) 

# training routes
# fungsi route untuk menangani
# permintaan API proses training
@menu.route('/training/perform/<path:target_param>', methods=['GET','POST'])
def training_perform(target_param):

    content_body = request.json
    input_layer = int(content_body["input_layer"]) if "input_layer" in content_body else (IMG_SIZE * IMG_SIZE)
    hidden_layer = int(content_body["hidden_layer"])  if "hidden_layer" in content_body else 100
    max_training_example = int(content_body["max_training_example"])  if "max_training_example" in content_body else MAX_TRAINING_EXAMPLE
    max_training_test = int(content_body["max_training_test"]) if "max_training_test" in content_body else MAX_TRAINING_TEST

    training_data = create_training_data(CLASSES, DATADIR, IMG_SIZE, target_param)

    X,y = make_X_and_y(training_data, input_layer)

    X_train,y_train = make_training_X_and_y(X,y,max_training_example)

    X_test,y_test = make_test_X_and_y(X,y,max_training_test)

    initial_Theta1,initial_Theta2 = initialize_theta(input_layer,hidden_layer)

    Theta1,Theta2 = make_training_theta(initial_Theta1,initial_Theta2,input_layer, hidden_layer, X_train, y_train)

    test, training = test_and_training(Theta1, Theta2, X_test, X_train)

    precision = get_precision(training,y_train)
    
    saving_training_model(target_param,Theta1,Theta2)

    return jsonify({
        'precision': precision,
        'target_param' : target_param,
        'test_accuration' : str(format((np.mean(test == y_test) * 100))),
        'training_accuration' : str(format((np.mean(training == y_train) * 100)))
    }), 200

# detect routes
# fungsi route untuk menangani
# dan memberikan respon untuk
# merender halaman deteksi
@menu.route('/detect', methods=['GET'])
def detect():
    return send_from_directory(os.path.join('templates','menu'), 'detect.html')

# detect routes
# fungsi route untuk menangani
# permintaan API proses deteksi
@menu.route('/detect/process/<path:target_param>', methods=['GET', 'POST'])
def detect_process(target_param):
    if request.method == 'POST':
        img_size = int(request.form["img_size"]) if "img_size" in request.form else IMG_SIZE
        file = request.files['file']

        if 'file' not in request.files:
            return jsonify({}), 500

        if not allowed_file(file.filename):
            return jsonify({}), 500

        vec = make_input_vector(file, img_size)

        Theta1,Theta2 = load_training_model(target_param)

        pred,acc = predict(Theta1, Theta2, vec)

        return jsonify({
            'target_param' : target_param,
            'prediction' : LABEL_NAMES[pred[0]],
            'accuration' : "{:f}".format(acc[pred[0]] * 100)
        }), 200

    return jsonify({}), 200

# fungsi untuk melist dataset gambar2
# yang akan dijadikan data training
# yang akan di resize dan di buat hitam putih
def create_training_data(classes, data_dir, img_size, param):
    result = []
    for clas in classes:
        path = os.path.join(data_dir,param,clas) 
        for img in os.listdir(path):
            try:
                img_array = cv2.imread(os.path.join(path,img) ,cv2.IMREAD_GRAYSCALE)
                new_array = cv2.resize(img_array, (img_size, img_size))
                result.append([new_array, classes.index(clas)])

            except OSError as e:
                print("OSErrroBad img most likely", e, os.path.join(path,img))

            except Exception as e:
               print("general exception", e, os.path.join(path,img))

    random.shuffle(result)
    return result

# fungsi untuk melist format
# file gambar aapa saja yang bisa 
# diolah berdfasarkan ekstensi file
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# fungsi untuk membuat variabel X dan y
# yang di ekstrak dari dataset
# yang setiap data akan di ubah ke numpy array
# dan di normalisasikan
def make_X_and_y(training_data, input_layer_size):
    X,y = [], []
    for features,label in training_data:
        X.append(features)
        y.append(label)
        
    X = np.array(X).reshape(-1, input_layer_size)
    X = X / 255

    return X,y


# fungsi untuk membuat array yang
# akan digunakan sebagai data training
def make_training_X_and_y(X,y,max_training_example):
    return X[:max_training_example, :], y[:max_training_example]

# fungsi untuk membuat array yang
# akan digunakan sebagai data testing
def make_test_X_and_y(X,y,max_training_test):
    return X[max_training_test:, :], y[max_training_test:]

# fungsi untuk meyiapkan theta
# akan digunakan sebagai model training
def initialize_theta(input_layer,hidden_layer):
    return initialise(hidden_layer, input_layer), initialise(Y_LABEL_SIZE, hidden_layer)

# fungsi untuk membuat theta
# akan digunakan sebagai model training
# menggunakan library dan skrip konfigurasi
# yang sering dipakai untuk neural network
def make_training_theta(initial_Theta1,initial_Theta2,input_layer_size, hidden_layer_size, X_train, y_train):
    maxiter = 100
    lambda_reg = 0.1
    myargs = (input_layer_size, hidden_layer_size, Y_LABEL_SIZE, X_train, y_train, lambda_reg)

    initial_nn_params = np.concatenate((initial_Theta1.flatten(), initial_Theta2.flatten()))
    results = minimize(neural_network, x0=initial_nn_params, args=myargs, options={'disp': True, 'maxiter': maxiter}, method="L-BFGS-B", jac=True)
    nn_params = results["x"]
    
    Theta1 = np.reshape(nn_params[:hidden_layer_size * (input_layer_size + 1)], (hidden_layer_size, input_layer_size + 1))
    Theta2 = np.reshape(nn_params[hidden_layer_size * (input_layer_size + 1):], (Y_LABEL_SIZE, hidden_layer_size + 1))

    return Theta1,Theta2

# fungsi untuk mengetest dan
# akan memberikan hasil training
# dan test terhadap model training
# yang telah di buat
def test_and_training(Theta1, Theta2, X_test, X_train):
    test, _ = predict(Theta1, Theta2, X_test)
    training, _ = predict(Theta1, Theta2, X_train)
    return test, training

# fungsi untuk mendapatkan presisi
# dengan mengunakan true positif dan false positif 
def get_precision(training,y_train):
    true_positive = 0
    for i in range(len(training)):
        if training[i] == y_train[i]:
            true_positive += 1
    false_positive = len(y_train) - true_positive
    return str(true_positive/(true_positive + false_positive))

# fungsi untuk menyimpan hasil training
# model yang nantinya akan digunakan kembali
# dalam proses deteksi
def saving_training_model(target_param,Theta1,Theta2):
    np.savetxt(os.path.join('app','training',target_param,'Theta1.csv'), Theta1, delimiter=",")
    np.savetxt(os.path.join('app','training',target_param,'Theta2.csv'), Theta2, delimiter=",")


# fungsi untuk mengambil hasil training
# model yang digunakan untuk proses deteksi
def load_training_model(target_param):
    Theta1 = np.loadtxt(os.path.join('app','training',target_param,'Theta1.csv'), delimiter=",")
    Theta2 = np.loadtxt(os.path.join('app','training',target_param,'Theta2.csv'), delimiter=",")
    return Theta1, Theta2

def make_input_vector(file, img_size):
    img_array = cv2.imdecode(np.fromstring(file.read(), np.uint8),cv2.IMREAD_GRAYSCALE) 
    new_array = cv2.resize(img_array, (img_size, img_size)) 
    vec = np.array(new_array).reshape(-1, img_size * img_size)
    vec = vec / 255
    return vec