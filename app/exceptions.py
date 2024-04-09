class UnsupportedProviderException(Exception):
    """Raised when oAuth provider is not supported"""


class AuthenticationException(Exception):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class UnauthorizedAccessException(Exception):
    def __init__(self, message="Unauthorized access"):
        super().__init__(message)


class ExerciseAlreadyExistsException(Exception):
    """Raised when attempting to create a custom exercise but it already exists"""
