from flask import Blueprint, render_template, jsonify
from ..config import logger as log
from ..libs.src.json.myJsonResponce import myJsonResponce, RESULT_STATUS

## Create Blueprint folder under "home"
home = Blueprint('home', __name__,
                   template_folder='templates',
                   static_folder='static')

# #############################################################
@home.route('/', methods=['GET'] )
def default():
    log.info ("Rendering 'home/default.html' page")
    return render_template('home/default.html')
# -------------------------------------------------------------
@home.route('/about', methods=['GET'] )
def about():
    """Render the INDEX page."""
    log.info ("Rendering 'home/about.html' page")
    return render_template('home/about.html')
# -------------------------------------------------------------
@home.route('/help', methods=['GET'] )
def help():
    """Render the ABOUT page."""
    log.info ("Rendering 'home/help.html' page")
    return render_template('home/help.html')
# #############################################################
@home.route('/status', methods=['GET']  )
def status():
    responce = myJsonResponce( RESULT_STATUS.INFO , "Server is running" , data=[])
    return jsonify( responce.to_dict() )