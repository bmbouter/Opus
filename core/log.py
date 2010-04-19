import logging # python standard library rocks!
import inspect
import sys
import os

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

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    stream = open(settings.LOG_DIR+"master.log", "a")
    handler = logging.StreamHandler(stream)
    formatter = MyFormatter()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    if log_to_stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        root_logger.addHandler(stdout_handler)

    logging.getLogger('boto').setLevel(logging.WARNING)

def getLogger():

    # Get the app name that is logging
    stack = inspect.stack()
    try:
        app_name = stack[1][0].f_globals["__package__"].split(".")[-1]
    finally:
        del stack

    log = logging.getLogger(app_name)
    if not log.handlers:
        stream = open(settings.LOG_DIR+app_name+".log", "a")
        handler = logging.StreamHandler(stream)
        formatter = MyFormatter()
        handler.setFormatter(formatter)
        log.addHandler(handler)

    return log
