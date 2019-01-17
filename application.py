### Define absolute path ###
import os 
APP_ROOT = os.path.dirname(os.path.abspath(__file__));

from flask import Flask
app = Flask(__name__);

#from routes import *
from app_routes import *


if __name__=="__main__":
    app.run(debug=True);