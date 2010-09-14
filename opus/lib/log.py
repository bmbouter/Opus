##############################################################################
# Copyright 2010 North Carolina State University                             #
#                                                                            #
#   Licensed under the Apache License, Version 2.0 (the "License");          #
#   you may not use this file except in compliance with the License.         #
#   You may obtain a copy of the License at                                  #
#                                                                            #
#       http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
#   Unless required by applicable law or agreed to in writing, software      #
#   distributed under the License is distributed on an "AS IS" BASIS,        #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#   See the License for the specific language governing permissions and      #
#   limitations under the License.                                           #
##############################################################################

"""Provides logging capabilities for applications in a Django environment.

Each application will have its own log file named "<app>.log".  In addition,
every log messsage will also be appended to "master.log".  These log files will
be located in the directory specified by the LOG_DIR Django setting.

If stdout is a tty, for example in the Django dev server, log messages will
also redirect to stdout using color coding for different levels.

Each application should get its own logger with the get_logger() function.  Here
is an example:

>>> import opus.lib.log
>>> log = opus.lib.log.get_logger("appname")
>>> log.debug("Debug Message here!")

This will put the message into two files: master.log and appname.log

This requires one to define a LOG_DIR setting in the Django settings.py. This
is the directory where the logs will be placed. Obviously the web server must
have write access to this directory.

"""

import logging # python standard library rocks!
import sys
import os
import os.path

from django.conf import settings

# Some cool code for colored logging:
# For background, add 40. For foreground, add 30
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORIZE = {
    #'INFO': WHITE,
    'DEBUG': BLUE,
}
HIGHLIGHT = {
    'CRITICAL': RED,
    'ERROR': RED,
    'WARNING': YELLOW,
}

class MyFormatter(logging.Formatter):
    """Used to format log messages all pretty like."""
    def __init__(self, color=True):
        logging.Formatter.__init__(self,
            '%(fileandlineno)-31s:%(funcName)s:%(asctime)s %(levelname)-8s %(message)s',
            "%Y-%m-%d %H:%M:%S"
        )
        self.use_color = color

    def format(self, record):

        record.pid = os.getpid()
        record.fileandlineno = "%s.%s:%s" % (record.name, record.filename, record.lineno)

        # Set the max length for the funcName field, and left justify
        l = 10
        record.funcName = ("%-" + str(l) + 's') % record.funcName[:l]

        levelname = record.levelname
        if self.use_color:
            if levelname in COLORIZE:
                # Colorize just the levelname
                # left justify again because the color sequence bumps it up
                # above 8 chars
                levelname_color = COLOR_SEQ % (30 + COLORIZE[levelname]) + "%-8s" % levelname + RESET_SEQ
                record.levelname = levelname_color
            elif levelname in HIGHLIGHT:
                # Colorize the entire line
                line = logging.Formatter.format(self, record)
                line = COLOR_SEQ % (40 + HIGHLIGHT[levelname]) + line + \
                        RESET_SEQ
                return line
        else:
            # Don't do anything for colorize, put some
            # stars before the line for highlight
            if levelname in HIGHLIGHT:
                line = logging.Formatter.format(self, record)
                line = "*" * min(79,len(line)) + "\n" + line
                return line

        return logging.Formatter.format(self, record)

def get_logger(name=None):
    """Gets a logger for use by Opus. If you want your log entries to also go
    to a separate file, give a name. Otherwise, log messages go to the master
    log"""
    opusroot = logging.getLogger("opus")

    try:
        logdir = settings.LOG_DIR
    except (AttributeError, ImportError):
        logdir = None

    try:
        loglevel = settings.LOG_LEVEL
    except (AttributeError, ImportError):
        loglevel = logging.DEBUG

    if isinstance(loglevel, basestring):
            loglevel = {"DEBUG":logging.DEBUG,
                        "INFO": logging.INFO,
                        "WARNING": logging.WARNING,
                        "ERROR": logging.ERROR,
                        "CRITICAL": logging.CRITICAL
                    }[loglevel.upper()]
    

    # If opusroot doesn't have any handlers, add one
    if not opusroot.handlers:
        opusroot.setLevel(loglevel)
        if logdir:
            masterlogfile = os.path.join(logdir, "master.log")
            masterhandler = logging.FileHandler(masterlogfile)
            masterhandler.setFormatter(MyFormatter(color=False))
            opusroot.addHandler(masterhandler)

        try:
            if hasattr(sys.stderr, "isatty"):
                istty = sys.stderr.isatty()
            else:
                istty = False
        except IOError:
            # mod_wsgi raises an error if std streams are accessed
            pass
        else:
            if istty:
                # Add a handler to stderr, using GLORIOUS EXTRA-COLOR!
                colorstderr = logging.StreamHandler()
                colorstderr.setFormatter(MyFormatter(color=True))
                opusroot.addHandler(colorstderr)

    if not name:
        return opusroot

    applogger = logging.getLogger("opus."+name)
    if not applogger.handlers:
        applogger.setLevel(loglevel)
        if logdir:
            # Set up a handler to a separate file
            applogfile = os.path.join(logdir, name+".log")
            h = logging.FileHandler(applogfile)
            h.setFormatter(MyFormatter(color=False))
            applogger.addHandler(h)

    return applogger
