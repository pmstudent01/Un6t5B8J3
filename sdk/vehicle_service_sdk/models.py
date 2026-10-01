"""Data models for the Vehicle Service SDK.

Mirrors the vehicle schema used in the Postman collection:
nickName, vin, make, model, year, miles.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class Vehicle:
    """Represents a vehicle resource."""

    nickName: str
    vin: str
    make: str
    model: str
    year: str
    miles: int
    id: Optional[Any] = None

    def to_dict(self, include_id: bool = False) -> Dict[str, Any]:
        """Serialize to a dict suitable for a request body.

        By default the ``id`` field is omitted, since it is server-assigned.
        """
        data = asdict(self)
        if not include_id:
            data.pop("id", None)
        else:
            if data.get("id") is None:
                data.pop("id", None)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Vehicle":
        """Build a Vehicle from an API response payload."""
        return cls(
            id=data.get("id"),
            nickName=data.get("nickName", ""),
            vin=data.get("vin", ""),
            make=data.get("make", ""),
            model=data.get("model", ""),
            year=str(data.get("year", "")),
            miles=data.get("miles", 0),
        )
