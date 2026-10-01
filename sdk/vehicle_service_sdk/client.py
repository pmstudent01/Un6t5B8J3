"""HTTP client for the Vehicle Service API.

Each method maps directly to a request in the Postman
"Vehicle Service Collection":

    create_vehicle   -> POST   /vehicles
    retrieve_vehicle -> GET    /vehicles/{id}
    update_vehicle   -> PATCH  /vehicles/{id}
    delete_vehicle   -> DELETE /vehicles/{id}
    list_vehicles    -> GET    /vehicles
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import requests

from .models import Vehicle
from .exceptions import VehicleServiceAPIError, VehicleNotFoundError


class VehicleServiceClient:
    """Client for the Vehicle Service REST API.

    :param base_url: Base URL of the service, e.g. ``http://localhost:8000``.
                     Corresponds to the ``{{baseUrl}}`` collection variable.
    :param api_key: Optional API key (sent as ``x-api-key`` header).
    :param timeout: Per-request timeout in seconds.
    :param session: Optional pre-configured ``requests.Session``.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._session = session or requests.Session()

    # -- internal helpers -------------------------------------------------

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _request(
        self,
        method: str,
        path: str,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        url = f"{self.base_url}{path}"
        headers = self._headers()
        if json_body is not None:
            headers["Content-Type"] = "application/json"

        response = self._session.request(
            method,
            url,
            headers=headers,
            json=json_body,
            timeout=self.timeout,
        )

        if not response.ok:
            self._raise_for_status(response)
        return response

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        try:
            body = response.json()
        except ValueError:
            body = response.text

        message = "Request failed"
        if isinstance(body, dict):
            message = body.get("message") or body.get("error") or message

        if response.status_code == 404:
            raise VehicleNotFoundError(response.status_code, message, body)
        raise VehicleServiceAPIError(response.status_code, message, body)

    @staticmethod
    def _as_body(vehicle: Union[Vehicle, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(vehicle, Vehicle):
            return vehicle.to_dict()
        return dict(vehicle)

    # -- API operations (one per collection request) ---------------------

    def create_vehicle(self, vehicle: Union[Vehicle, Dict[str, Any]]) -> Vehicle:
        """POST /vehicles — Create a vehicle. Returns the created vehicle."""
        response = self._request("POST", "/vehicles", json_body=self._as_body(vehicle))
        return Vehicle.from_dict(response.json())

    def list_vehicles(self) -> List[Vehicle]:
        """GET /vehicles — Get all vehicles."""
        response = self._request("GET", "/vehicles")
        data = response.json()
        if isinstance(data, dict) and "vehicles" in data:
            data = data["vehicles"]
        return [Vehicle.from_dict(item) for item in data]

    def retrieve_vehicle(self, vehicle_id: Any) -> Vehicle:
        """GET /vehicles/{id} — Retrieve a single vehicle by id."""
        response = self._request("GET", f"/vehicles/{vehicle_id}")
        return Vehicle.from_dict(response.json())

    def update_vehicle(
        self, vehicle_id: Any, changes: Union[Vehicle, Dict[str, Any]]
    ) -> Vehicle:
        """PATCH /vehicles/{id} — Partially update a vehicle."""
        response = self._request(
            "PATCH", f"/vehicles/{vehicle_id}", json_body=self._as_body(changes)
        )
        return Vehicle.from_dict(response.json())

    def delete_vehicle(self, vehicle_id: Any) -> None:
        """DELETE /vehicles/{id} — Delete a vehicle. Returns None on success."""
        self._request("DELETE", f"/vehicles/{vehicle_id}")

    # -- convenience ------------------------------------------------------

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "VehicleServiceClient":
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()
