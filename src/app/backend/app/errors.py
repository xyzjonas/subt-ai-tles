class ServiceError(Exception):
    """Base for business-logic errors; mapped to HTTP responses in main.py."""


class NotFoundError(ServiceError):
    pass


class ConflictError(ServiceError):
    pass


class InvalidInputError(ServiceError):
    pass
