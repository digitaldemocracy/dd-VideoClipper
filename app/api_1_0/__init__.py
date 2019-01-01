from flask import Blueprint

api = Blueprint('api', __name__)

from . import dd_video_api, errors

