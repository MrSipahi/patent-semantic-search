from flask import Flask
from .resources import Patent
from flask_cors import CORS
from waitress import serve
import os 
from dotenv import load_dotenv



class API():
    def __init__(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(Patent.patent_bp, url_prefix='/patent')
        CORS(self.app)

        load_dotenv(".env")
        self.is_prod= os.getenv("IS_PROD", "False").lower() == "true"



    def start(self):

        if self.is_prod:
            this_files_dir = os.path.dirname(os.path.abspath(__file__))
            os.chdir(this_files_dir)

            serve(self.app, host='127.0.0.1', port=8080)
        else:
            self.app.run(debug=True, host="0.0.0.0", port=8080)


