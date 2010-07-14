"""Provides logging capabilities for applications in a Django environment.

Each application will have its own log file named "<app>.log".  In addition,
every log messsage will also be appended to "master.log".  These log files will
be located in the directory specified by the LOG_DIR Django setting.

If stdout is a tty, for example in the Django dev server, log messages will
also redirect to stdout using color coding for different levels.

Each application should get its own logger with the getLogger() function.  Here
is an example:

>>> import opus.lib.log
>>> log = opus.lib.log.getLogger()
>>> log.debug("Debug Message here!")

This will put the message into two files: master.log and appname.log

This requires one to define a LOG_DIR setting in the Django settings.py. This
is the directory where the logs will be placed. Obviously the web server must
have write access to this directory.

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

# Assume true until _init_logging tries to do the import
django_context = True

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

def _init_logging():
    """Initializes Opus's logging

    This is called the first time a logger is requested

    """
    global django_context

    if "OPUS_LOGGING_DISABLE" in os.environ:
        # Private hook so Opus can disable logging in situations where logging
        # would fail, such as when Opus calls syncdb on a project.
        root_logger = logging.getLogger()
        class NullHandler(logging.Handler):
            def emit(self, record):
                pass
        root_logger.addHandler(NullHandler)
        django_context = False
        return

    try:
        settings.LOG_DIR
    except AttributeError:
        # Not running in a Django context, can't set up the master log file.
        django_context = False


    # Configure a handler for the root logger
    root_logger = logging.getLogger()
    if django_context:
        handler = logging.FileHandler(
                os.path.join(settings.LOG_DIR, "master.log"),
                "a")
        handler.setFormatter( MyFormatter( color=False) )
        root_logger.addHandler(handler)

    # Configure second handler for the root logger to stdout if it's a console
    try:
        if sys.stdout.isatty():
            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setFormatter( MyFormatter(color=True) )
            root_logger.addHandler(stdout_handler)
    except IOError:
        # mod_wsgi may raise an error if we try to access stdout
        pass

    if not django_context:
        # Just set it to debug and be done with it
        root_logger.setLevel(logging.DEBUG)
        return

    # Set logging level. Attempt to get settings.LOG_LEVEL and set log level to
    # that. If it's not an int or a string matching one of the 5 standard log
    # levels, or if LOG_LEVEL isn't defined, logging is set to DEBUG or INFO
    # depending on settings.DEBUG
    def fallback():
        if settings.DEBUG:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        return log_level
    try:
        level = settings.LOG_LEVEL
    except AttributeError:
        log_level = fallback()
    else:
        if isinstance(level, basestring):
            try:
                log_level = {"DEBUG":logging.DEBUG,
                            "INFO": logging.INFO,
                            "WARNING": logging.WARNING,
                            "ERROR": logging.ERROR,
                            "CRITICAL": logging.CRITICAL
                        }[level.upper()]
            except KeyError:
                log_level = fallback()
        elif isinstance(level, (int,long)):
                log_level = level
        else:
            log_level = fallback()

    root_logger.setLevel(log_level)

def getLogger(appname=None):
    """Returns the application's logger

    This is called by each application to get their logging object.  It returns
    a different logger based on which application called it.  The application
    can then use standard python logging, for example:
    >>> import opus.lib.log
    >>> log = opus.lib.log.getLogger()
    >>> log.debug("Debug Message here!")

    appname, if specified, will be used for the application log file.
    Otherwise, the appname will be determined using inspect.stack() to look up
    one frame in the stack call.

    """
    if len(logging.getLogger().handlers) == 0:
        _init_logging()

    # Get the app name that is logging
    if appname:
        app_name = appname
    else:
        stack = inspect.stack()
        try:
            app_name = stack[1][0].f_globals["__package__"].split(".")[-1]
        finally:
            del stack

    log = logging.getLogger(app_name)

    # Add a handler if it doesn't already exist
    if len(log.handlers) == 0 and django_context:
        handler = logging.FileHandler(
                os.path.join(settings.LOG_DIR, app_name+".log"),
                'a')
        handler.setFormatter( MyFormatter(color=False) )
        log.addHandler(handler)

    return log

# A more PEP8 name:
get_logger = getLogger
