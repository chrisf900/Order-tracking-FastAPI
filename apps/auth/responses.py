from fastapi import HTTPException, status


class BaseErrorResponse(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "API_OAUTH_INTERNAL_ERROR"
    headers = {"WWW-Authenticate": "Bearer"}

    def __init__(self):
        super().__init__(detail=self.detail, status_code=self.status_code)


class APIIncorrectUserOrPasswordError(BaseErrorResponse):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect Username or Password"


class APICredentialError(BaseErrorResponse):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Could not Validate Credentials"


class APIUserPermissionsError(BaseErrorResponse):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "User does not have permissions"
