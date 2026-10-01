"""Exceptions raised by the Vehicle Service SDK."""

from __future__ import annotations

from typing import Any, Optional


class VehicleServiceError(Exception):
    """Base class for all SDK errors."""


class VehicleServiceAPIError(VehicleServiceError):
    """Raised when the API returns a non-success status code."""

    def __init__(self, status_code: int, message: str, body: Optional[Any] = None):
        self.status_code = status_code
        self.body = body
        super().__init__(f"[{status_code}] {message}")


class VehicleNotFoundError(VehicleServiceAPIError):
    """Raised when a vehicle is not found (HTTP 404)."""
