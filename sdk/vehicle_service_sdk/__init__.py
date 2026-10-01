"""Vehicle Service SDK.

A lightweight Python client for the Vehicle Service REST API,
generated from the Postman "Vehicle Service Collection".

Usage::

    from vehicle_service_sdk import VehicleServiceClient, Vehicle

    client = VehicleServiceClient(base_url="http://localhost:8000")
    vehicles = client.list_vehicles()
"""

from .client import VehicleServiceClient
from .models import Vehicle
from .exceptions import (
    VehicleServiceError,
    VehicleNotFoundError,
    VehicleServiceAPIError,
)

__all__ = [
    "VehicleServiceClient",
    "Vehicle",
    "VehicleServiceError",
    "VehicleNotFoundError",
    "VehicleServiceAPIError",
]

__version__ = "1.0.0"
