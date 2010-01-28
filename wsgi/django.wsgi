import os
import sys

parent_directory = '/'.join( os.path.abspath(__file__).split('/')[:-2] )
sys.path.append( parent_directory )

import django.core.handlers.wsgi
from django.conf import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
application = django.core.handlers.wsgi.WSGIHandler()
settings.LOG_FILE = settings.BASE_DIR+"/log/vdi.log"
