from flask import Blueprint
from app import *

# Kanban Blueprint
planner = Blueprint('planner', __name__, url_prefix='/planner')

# Import all endpoints
from controllers.course_controller import *
