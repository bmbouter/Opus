# Follows suggestions given here:
# http://docs.python.org/library/logging.html#configuring-logging-for-a-library
import logging
log = logging.getLogger("deltacloud")
class NullHandler(logging.Handler):
    def emit(self, recond):
        pass
log.addHandler(NullHandler())
