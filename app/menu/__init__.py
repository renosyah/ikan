from flask import Blueprint

menu = Blueprint('menu', __name__)

from . import routes
