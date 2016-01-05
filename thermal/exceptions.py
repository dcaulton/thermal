class ThermalBaseError(Exception):

    """
    Invalid request at the resource or parameter level; the client is using the API wrong.
    """
    status_code = 400

class NotFoundError(ThermalBaseError):

    """
    The user asked for something that doesn't exist.
    """
    status_code = 404

