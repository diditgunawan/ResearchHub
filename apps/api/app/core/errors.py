from typing import Optional, Any, Dict
from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception following RFC 7807 problem details specification."""
    def __init__(
        self,
        status_code: int,
        code: str,
        title: str,
        detail: str,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.code = code
        self.title = title
        self.detail = detail
        self.data = data or {}
        super().__init__(detail)


class NotFoundError(AppException):
    def __init__(self, detail: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(404, code, "Not Found", detail)


class UnauthorizedError(AppException):
    def __init__(self, detail: str = "Authentication required", code: str = "UNAUTHORIZED"):
        super().__init__(401, code, "Unauthorized", detail)


class ForbiddenError(AppException):
    def __init__(self, detail: str = "Insufficient permissions", code: str = "FORBIDDEN"):
        super().__init__(403, code, "Forbidden", detail)


class ConflictError(AppException):
    def __init__(self, detail: str = "Resource conflict", code: str = "CONFLICT"):
        super().__init__(409, code, "Conflict", detail)


class BadRequestError(AppException):
    def __init__(self, detail: str = "Invalid request", code: str = "BAD_REQUEST"):
        super().__init__(400, code, "Bad Request", detail)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """RFC 7807 formatted exception response."""
    request_id = getattr(request.state, "request_id", "unknown")
    content = {
        "type": "about:blank",
        "title": exc.title,
        "status": exc.status_code,
        "detail": exc.detail,
        "instance": str(request.url),
        "code": exc.code,
        "request_id": request_id,
    }
    if exc.data:
        content["errors"] = exc.data
    return JSONResponse(status_code=exc.status_code, content=content)
