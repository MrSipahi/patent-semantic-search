from distutils.sysconfig import get_makefile_filename
from flask import Blueprint
from flask_restful import Api

from .Patent import Patent, Search


patent_bp = Blueprint('patent', __name__)
api_patent = Api(patent_bp)
api_patent.add_resource(Patent, '/<int:patent_id>')
api_patent.add_resource(Search, '/search')
