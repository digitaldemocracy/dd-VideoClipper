activate_this = '/var/www/video_editor/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import sys, os
sys.path.insert (0,'/var/www/video_editor')
from app import create_app
application = create_app(os.getenv('FLASK_CONFIG') or 'default')
