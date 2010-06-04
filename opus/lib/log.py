"""Allows applications to create a log.

Each application will have its own log file named "<app>.log".  In addition,
every log messsage will also be optionally appended to "master.log".  These log
files will be located in the directory specified by the LOG_DIR setting.

Each application has to get its own logger with the core.log.getLogger() function.  Here is an example:

>>> import core
>>> log = core.log.getLogger()
>>> log.debug("Debug Message here!")

"""

import logging # python standard library rocks!
import inspect
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
    def __init__(self, use_color = True):
        logging.Formatter.__init__(self,
            '%(fileandlineno)-19s:%(funcName)s:%(pid)5s:%(asctime)s %(levelname)-8s %(message)s',
            "%Y-%m-%d %H:%M:%S"
        )
        self.use_color = use_color

    def format(self, record):

        record.pid = os.getpid()
        record.fileandlineno = "%s:%s" % (record.filename, record.lineno)

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

def init_logging(log_to_stdout=True):
    """Initializes Opus's logging

    This is called before any of the applications get started to set up
    logging.  If you don't want the log to be repeated to stdout, then specify
    log_to_stdout=False.

    """

    root_logger = logging.getLogger()
    stream = open(settings.LOG_DIR+"master.log", "a")
    handler = logging.StreamHandler(stream)
    formatter = MyFormatter()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    if log_to_stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        root_logger.addHandler(stdout_handler)

    # Set logging level
    if settings.LOG_LEVEL.upper() == "DEBUG":
        log_level = logging.DEBUG
    elif settings.LOG_LEVEL.upper() == "INFO":
        log_level = logging.INFO
    elif settings.LOG_LEVEL.upper() == "WARNING":
        log_level = logging.WARNING
    elif settings.LOG_LEVEL.upper() == "ERROR":
        log_level = logging.ERROR
    elif settings.LOG_LEVEL.upper() == "CRITICAL":
        log_level = logging.CRITICAL
    else:
        root_logger.error('LOG_LEVEL should be one of: DEBUG, INFO, WARNING, ERROR or CRITICAL.  Instead it is "%s"' % settings.LOG_LEVEL)
        root_logger.error('Setting LOG_LEVEL to DEBUG')
        log_level = logging.DEBUG
        # TODO: What should be done now?
    root_logger.setLevel(log_level)

    # Ignore messages from boto that we don't care about
    logging.getLogger('boto').setLevel(logging.WARNING)

def getLogger():
    """Returns the application's logger

    This is called by each application to get their logging object.  It returns
    a different logger baised on which application called it.  The application
    can then use standard python logging, for example:
    >>> import core
    >>> log = core.log.getLogger()
    >>> log.debug("Debug Message here!")

    """

    # Get the app name that is logging
    stack = inspect.stack()
    try:
        app_name = stack[1][0].f_globals["__package__"].split(".")[-1]
    finally:
        del stack

    log = logging.getLogger(app_name)

    # Add a handler if it doesn't already exist
    if not log.handlers:
        stream = open(settings.LOG_DIR+app_name+".log", "a")
        handler = logging.StreamHandler(stream)
        formatter = MyFormatter()
        handler.setFormatter(formatter)
        log.addHandler(handler)

    return log
