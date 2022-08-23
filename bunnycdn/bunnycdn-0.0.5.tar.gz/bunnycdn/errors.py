class ValidationError(Exception):
    """ Exception raised for errors in the input. """
    pass

class APIError(Exception):
    """
    Base class for all API errors.
    """
    pass

class NotAuthorized(APIError):
    """
    Raised when the caller is not authorized to perform the action.
    """
    pass

class NotFound(APIError):
    """
    Raised when the requested resource is not found.
    """
    pass

class BadRequest(APIError):
    """
    Raised when the caller made a bad request.
    """
    pass

class InternalServerError(APIError):
    """
    Raised when the server encountered an error.
    """
    pass
