from flask import Blueprint

blueprint = Blueprint("blueprint", __name__)

from .basics import *
from .web import *