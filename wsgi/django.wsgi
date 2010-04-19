import os
import sys

parent_directory = '/'.join( os.path.abspath(__file__).split('/')[:-2] )
sys.path.append( parent_directory )

import django.core.handlers.wsgi
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# WSGI doesn't run __init__.py for some reason.  Oh well...
import core
core.log.init_logging(False)

application = django.core.handlers.wsgi.WSGIHandler()
