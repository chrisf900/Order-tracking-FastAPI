from fastapi import status
from fastapi.responses import JSONResponse


class BaseErrorResponse(JSONResponse):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error = "API_INTERNAL_ERROR"

    def __init__(self):
        content = {"detail": self.error}
        super().__init__(content=content, status_code=self.status_code)


class APIOrderDoesNotExistError(BaseErrorResponse):
    status_code = status.HTTP_404_NOT_FOUND
    error = "API_ORDER_NOT_FOUND_ERROR"


class APIInvalidDeliveryStatusTransition(BaseErrorResponse):
    status_code = status.HTTP_409_CONFLICT
    error = "API_INVALID_DELIVERY_STATUS_TRANSITION"


class APIDeleteProductsIsNotAvailableError(BaseErrorResponse):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    error = "API_PRODUCTS_CANNOT_BE_DELETED"


class APICancelOrderIsNotAvailableError(BaseErrorResponse):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    error = "API_ORDER_CANNOT_BE_DELETED"


class APIUserNotFoundError(BaseErrorResponse):
    status_code = status.HTTP_404_NOT_FOUND
    error = "API_USER_NOT_FOUND"


class APIUserAlreadyExistsError(BaseErrorResponse):
    status_code = status.HTTP_400_BAD_REQUEST
    error = "API_USER_ALREADY_EXISTS"


class APIEmailAlreadyRegisteredError(BaseErrorResponse):
    status_code = status.HTTP_400_BAD_REQUEST
    error = "API_EMAIL_ALREADY_REGISTERED"
