from __future__ import annotations


class SmartBankError(Exception):
    status_code: int = 500
    code: str = "INTERNAL_ERROR"
    detail: str = "An internal error occurred"


class NotFoundError(SmartBankError):
    status_code = 404
    code = "NOT_FOUND"

    def __init__(self, resource: str = "Resource") -> None:
        self.detail = f"{resource} not found"


class ValidationError(SmartBankError):
    status_code = 400
    code = "VALIDATION_ERROR"

    def __init__(self, detail: str = "Invalid input") -> None:
        self.detail = detail


class AuthenticationError(SmartBankError):
    status_code = 401
    code = "AUTHENTICATION_ERROR"

    def __init__(self, detail: str = "Invalid credentials") -> None:
        self.detail = detail


class AuthorizationError(SmartBankError):
    status_code = 403
    code = "FORBIDDEN"

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        self.detail = detail


class RateLimitError(SmartBankError):
    status_code = 429
    code = "RATE_LIMIT_EXCEEDED"

    def __init__(self, detail: str = "Too many requests") -> None:
        self.detail = detail


class DocumentProcessingError(SmartBankError):
    status_code = 422
    code = "DOCUMENT_PROCESSING_ERROR"

    def __init__(self, detail: str = "Failed to process document") -> None:
        self.detail = detail
