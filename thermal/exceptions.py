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

class DocumentConfigurationError(ThermalBaseError):

    """
    The user is trying to do something with a document which will break referential integrity, change
    the type of a document, or something else which will cause havoc in our db and system.
    """
    status_code = 409
