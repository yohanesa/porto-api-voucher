from .base import BaseError

class AuthError(BaseError):
    code = "401"
    message = "Invalid username or password"

class IsNotAuthenticated(BaseError):
    code = "401"
    message = "Not Authenticated"

class IsNotAuthorized(BaseError):
    code = "403"
    message = "Not Authorized"

class UserDisabled(BaseError):
    code = "403"
    message = "User is disabled or banned"