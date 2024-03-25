class UnsupportedProviderException(Exception):
    """Raised when oAuth provider is not supported"""


class InvalidAuthCredentialsException(Exception):
    """Raised when credentials given cannot be authenticated"""
