"""
Volt Core Platform Custom Exceptions & Error Handlers
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class VoltException(Exception):
    """Base exception for all Volt Platform domain errors."""

    def __init__(
        self,
        message: str,
        code: str = "VOLT_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(VoltException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' was not found.",
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": str(identifier)},
        )


class ValidationError(VoltException):
    """Raised when data contract or validation checks fail."""

    def __init__(self, message: str, errors: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DATA_VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=errors or {},
        )


class FeatureStoreError(VoltException):
    """Raised when an operation on the Feature Store fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="FEATURE_STORE_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details or {},
        )


class ModelRegistryError(VoltException):
    """Raised when a model vault or registry operation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="MODEL_REGISTRY_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details or {},
        )


class PipelineExecutionError(VoltException):
    """Raised when a data or ML execution pipeline fails."""

    def __init__(self, pipeline_id: str, stage: str, reason: str):
        super().__init__(
            message=f"Pipeline '{pipeline_id}' failed at stage '{stage}': {reason}",
            code="PIPELINE_EXECUTION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"pipeline_id": pipeline_id, "stage": stage, "reason": reason},
        )


class UnauthorizedError(VoltException):
    """Raised for authentication or access control failures."""

    def __init__(self, message: str = "Invalid credentials or unauthorized access"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(VoltException):
    """Raised when user has insufficient privileges."""

    def __init__(self, message: str = "Insufficient permissions to perform this operation"):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
        )
