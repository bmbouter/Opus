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

"""This package contains profiling related code for the logging of performance
related data.

"""

import datetime
import os.path

from django.core.handlers.wsgi import WSGIHandler


class OpusWSGIHandler(WSGIHandler):
    """Wrapper around the Django WSGIHandler. As per the WSGI protocol, each
    call to __call__ returns an iterator object (django.http.HttpResponse)
    where each item in the iterator is a string.

    Use this instead of the Django WSGIHandler in the wsgi entry point file to
    log each request and response time.

    """
    def __init__(self, *args, **kwargs):
        super(OpusWSGIHandler, self).__init__(*args, **kwargs)

    def __call__(self, environ, start_response):
        from opus.lib.profile.profilerapp.models import Request
        request_info = Request()
        request_info.timestamp = datetime.datetime.now()
        request_info.uri = environ['PATH_INFO']
        request_info.method = environ['REQUEST_METHOD']
        
        response = super(OpusWSGIHandler, self).__call__(environ, start_response)

        # Insert our own close method into the response object
        origclose = response.close
        def newclose():
            origclose()
            response_time = datetime.datetime.now() - request_info.timestamp
            request_info.responsetime = \
                    response_time.seconds + response_time.microseconds * 1e-6
            request_info.save()


        response.close = newclose
        return response

