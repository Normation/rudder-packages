# This is ncf_api_flask_app.wsgi
#
# It is the main entry point for the ncf api WSGI environment,
# importing the necessary elements like the Python virtualenv
# and the ncf api itself.
#

# Import core modules
import sys

# Set up paths
ncf_path = '/usr/share/ncf/api'
virtualenv_path = '/usr/share/ncf-api-virtualenv'

# Virtualenv initialization
activate_this = virtualenv_path + '/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

# Append ncf API path to the current one
sys.path.append(ncf_path)

# Launch ncf_api_flask_app
from ncf_api_flask_app import app as application
