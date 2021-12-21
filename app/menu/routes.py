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

LABEL_NAMES = ["Segar","Agak Segar","Busuk"]
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}
IMG_SIZE = 28
DATADIR = os.path.join("app","dataset")
CLASSES = ["0","1","2"]
MAX_TRAINING_EXAMPLE = 400
MAX_TRAINING_TEST = 300
Y_LABEL_SIZE = 3

@menu.after_request
def add_header(response):
    response.cache_control.max_age = -1
    return response

@menu.route('/<path:folder_name>/<path:filename>', methods=['GET'])
def serve_static(folder_name,filename):
    return send_from_directory(os.path.join('files',folder_name), filename)



## index routes
@menu.route('/', methods=['GET'])
def index():
    return render_template('menu/index.html')





## training routes
@menu.route('/training', methods=['GET'])
def training():
    return send_from_directory(os.path.join('templates','menu'), 'training.html')

@menu.route('/training/<path:target_param>', methods=['GET','POST'])
def training_model(target_param):
    return jsonify({'is_exist': os.path.exists(os.path.join('app','training',target_param,'Theta1.csv')),'target_param' : target_param}) 

@menu.route('/training/perform/<path:target_param>', methods=['GET','POST'])
def training_perform(target_param):

    content_body = request.json
    input_layer = int(content_body["input_layer"]) if "input_layer" in content_body else (IMG_SIZE * IMG_SIZE)
    hidden_layer = int(content_body["hidden_layer"])  if "hidden_layer" in content_body else 100
    max_training_example = int(content_body["max_training_example"])  if "max_training_example" in content_body else MAX_TRAINING_EXAMPLE
    max_training_test = int(content_body["max_training_test"]) if "max_training_test" in content_body else MAX_TRAINING_TEST

    training_data = create_training_data(CLASSES, DATADIR, IMG_SIZE, target_param)
    random.shuffle(training_data)

    X = []
    y = []

    for features,label in training_data:
        X.append(features)
        y.append(label)

    X = np.array(X).reshape(-1,IMG_SIZE * IMG_SIZE)

    # Normalizing the data
    X = X / 255

    # Splitting data into training set with 60,000 examples
    X_train = X[:max_training_example, :]
    y_train = y[:max_training_example]
    
    # Splitting data into testing set with 10,000 examples
    X_test = X[max_training_test:, :]
    y_test = y[max_training_test:]
    
    m = X.shape[0]
    input_layer_size = input_layer
    hidden_layer_size = hidden_layer
    num_labels = Y_LABEL_SIZE
    
    # Randomly initialising Thetas
    initial_Theta1 = initialise(hidden_layer_size, input_layer_size)
    initial_Theta2 = initialise(num_labels, hidden_layer_size)
    
    # Unrolling parameters into a single column vector
    initial_nn_params = np.concatenate((initial_Theta1.flatten(), initial_Theta2.flatten()))
    maxiter = 100
    lambda_reg = 0.1  # To avoid overfitting
    myargs = (input_layer_size, hidden_layer_size, num_labels, X_train, y_train, lambda_reg)
    
    # Calling minimize function to minimize cost function and to train weights
    results = minimize(neural_network, x0=initial_nn_params, args=myargs, options={'disp': True, 'maxiter': maxiter}, method="L-BFGS-B", jac=True)
    
    nn_params = results["x"]  # Trained Theta is extracted
    
    # Weights are split back to Theta1, Theta2
    Theta1 = np.reshape(nn_params[:hidden_layer_size * (input_layer_size + 1)], (hidden_layer_size, input_layer_size + 1))  # shape = (100, 785)
    Theta2 = np.reshape(nn_params[hidden_layer_size * (input_layer_size + 1):], (num_labels, hidden_layer_size + 1))  # shape = (10, 101)

    # Checking test set accuracy of our model
    test,_ = predict(Theta1, Theta2, X_test)

    # Checking train set accuracy of our model
    training,_ = predict(Theta1, Theta2, X_train)

    # Evaluating precision of our model
    true_positive = 0
    for i in range(len(training)):
        if training[i] == y_train[i]:
            true_positive += 1
    false_positive = len(y_train) - true_positive
    
    # Saving Thetas in .txt file
    np.savetxt(os.path.join('app','training',target_param,'Theta1.csv'), Theta1, delimiter=",")
    np.savetxt(os.path.join('app','training',target_param,'Theta2.csv'), Theta2, delimiter=",")

    return jsonify({'precision':str(true_positive/(true_positive + false_positive)),'target_param' : target_param, 'test_accuration' : str(format((np.mean(test == y_test) * 100))), 'training_accuration' : str(format((np.mean(training == y_train) * 100)))}), 200


def create_training_data(classes, data_dir, img_size, param):
    result = []
    for clas in classes:
        path = os.path.join(data_dir,param,clas) 
        for img in os.listdir(path):  # iterate over each image
            try:
                img_array = cv2.imread(os.path.join(path,img) ,cv2.IMREAD_GRAYSCALE)  # convert to array
                new_array = cv2.resize(img_array, (img_size, img_size))  # resize to normalize data size
                result.append([new_array, classes.index(clas)])  # add this to our training_data
            except Exception as e:  # in the interest in keeping the output clean...
                pass 
    return result




## detect routes
@menu.route('/detect', methods=['GET'])
def detect():
    return send_from_directory(os.path.join('templates','menu'), 'detect.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@menu.route('/detect/process/<path:target_param>', methods=['GET', 'POST'])
def detect_process(target_param):
    if request.method == 'POST':
        img_size = int(request.form["img_size"]) if "img_size" in request.form else IMG_SIZE
        file = request.files['file']

        if 'file' not in request.files:
            return jsonify({}), 500

        if not allowed_file(file.filename):
            return jsonify({}), 500

        img_array = cv2.imdecode(np.fromstring(file.read(), np.uint8),cv2.IMREAD_GRAYSCALE) 
        new_array = cv2.resize(img_array, (img_size, img_size)) 
        vec = np.array(new_array).reshape(-1, img_size * img_size)
        vec = vec / 255

        # Loading Thetas
        Theta1 = np.loadtxt(os.path.join('app','training',target_param,'Theta1.csv'), delimiter=",")
        Theta2 = np.loadtxt(os.path.join('app','training',target_param,'Theta2.csv'), delimiter=",")

        # Calling function for prediction
        pred,acc = predict(Theta1, Theta2, vec)

        return jsonify({'target_param' : target_param, 'prediction' : LABEL_NAMES[pred[0]], 'accuration' : "{:f}".format(acc[pred[0]] * 100)}), 200

    return jsonify({}), 200