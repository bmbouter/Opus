"""This package contains profiling related code for the logging of performance
related data.

"""

import time
import os.path

from django.core.handlers.wsgi import WSGIHandler


class OpusWSGIHandler(WSGIHandler):
    """Wrapper around the Django WSGIHandler. As per the WSGI protocol, each
    call to __call__ returns an iterator object (django.http.HttpResponse)
    where each item in the iterator is a string.

    Also as per the WSGI protocol, the web server must call close() after the
    response has finished. Since Django uses a persistant object for every
    request, we cannot guarantee the order in which the __call__() and close()
    methods are called if the server is threaded.

    """
    def __init__(self, *args, **kwargs):
        super(OpusWSGIHandler, self).__init__(*args, **kwargs)

    def __call__(self, environ, start_response):
        timestamp = time.time()
        request_uri = environ['PATH_INFO']
        request_method = environ['REQUEST_METHOD']
        
        result = super(OpusWSGIHandler, self).__call__(environ, start_response)

        # Insert a close method for the response object
        origclose = result.close
        def close():
            origclose()
            response_time = time.time() - timestamp
            from django.conf import settings
            with open(os.path.join(settings.LOG_DIR, "request.log"), 'a') as f:
                f.write("{0}:{1}:{2}:{3}\n".format(
                    timestamp,
                    response_time,
                    request_method,
                    request_uri,
                    ))

        result.close = close
        return result

