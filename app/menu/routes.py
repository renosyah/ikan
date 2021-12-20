from flask import request, render_template, send_from_directory
from . import menu
import os

@menu.after_request
def add_header(response):
    response.cache_control.max_age = -1
    return response

@menu.route('/<path:folder_name>/<path:filename>', methods=['GET'])
def serve_static(folder_name,filename):

    return send_from_directory(os.path.join('files',folder_name), filename)

@menu.route('/', methods=['GET'])
def index():
    return render_template('menu/index.html', )