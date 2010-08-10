class Error(Exception):
    """Base exception for ``opus.lib.prov`` errors"""
    pass

class ParsingError(Error):
    """
    Exception raised by a driver when it has trouble parsing a response from
    a server.
    
    """
    pass

class ServerError(Error):
    """
    Exception raised by a driver when a server gives an unexpected response, such as "404 Not Found" error.

    """
    pass
