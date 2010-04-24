"""The entry point for a wsgi server to use Opus."""

import os
import sys

parent_directory = '/'.join( os.path.abspath(__file__).split('/')[:-2] )
sys.path.append( parent_directory )

import django.core.handlers.wsgi
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# WSGI doesn't run __init__.py for some reason.
# We need to call init_logging from here anyways to disable logs getting
# repeated to stdout.
import core
core.log.init_logging(False)

# This is the actual object which the wsgi server will look at
application = django.core.handlers.wsgi.WSGIHandler()
