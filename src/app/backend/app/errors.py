from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable identifiers the frontend maps to localized messages. Never rename a value."""

    INVALID_CREDENTIALS = "invalid_credentials"
    PASSWORD_CHANGE_REQUIRED = "password_change_required"  # noqa: S105
    ADMIN_ONLY = "admin_only"

    QUOTA_EXCEEDED = "quota_exceeded"
    MODEL_NOT_OFFERED = "model_not_offered"
    MODEL_WITHOUT_RATE = "model_without_rate"

    JOB_NOT_FOUND = "job_not_found"
    CUE_NOT_FOUND = "cue_not_found"
    USER_NOT_FOUND = "user_not_found"
    JOB_NOT_PROCESSING = "job_not_processing"
    TRANSLATION_NOT_READY = "translation_not_ready"

    FILE_NOT_SRT = "file_not_srt"
    FILE_TOO_LARGE = "file_too_large"
    FILE_NOT_UTF8 = "file_not_utf8"
    FILE_INVALID_SRT = "file_invalid_srt"
    FILE_EMPTY = "file_empty"
    SAME_LANGUAGE = "same_language"
    UNKNOWN_LANGUAGE = "unknown_language"

    USERNAME_TAKEN = "username_taken"
    LAST_ADMIN = "last_admin"
    CANNOT_DELETE_SELF = "cannot_delete_self"
    WRONG_CURRENT_PASSWORD = "wrong_current_password"  # noqa: S105
    PASSWORD_UNCHANGED = "password_unchanged"  # noqa: S105

    TRANSLATION_NOT_CONFIGURED = "translation_not_configured"
    TRANSLATION_BUSY = "translation_busy"
    TRANSLATION_FAILED = "translation_failed"
    TRANSLATION_QUEUE_FAILED = "translation_queue_failed"


class ServiceError(Exception):
    """Base for business-logic errors; mapped to HTTP responses in main.py.

    `code` is the contract with the frontend, `message` an English fallback for logs and
    API consumers, `params` the values a localized message may interpolate.
    """

    def __init__(self, code: ErrorCode, message: str, **params: str | int) -> None:
        super().__init__(message)
        self.code = code
        self.params = params


class NotFoundError(ServiceError):
    pass


class ConflictError(ServiceError):
    pass


class InvalidInputError(ServiceError):
    pass


class QuotaExceededError(ServiceError):
    pass


class UpstreamError(ServiceError):
    pass


class UnauthorizedError(ServiceError):
    pass


class ForbiddenError(ServiceError):
    pass
