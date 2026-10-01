"""Vehicle Service API — reference implementation.

A standalone HTTP server implementing the Vehicle Service API exactly as
described by the Postman "Vehicle Service Collection":

    POST   /vehicles        -> 201 Create a vehicle
    GET    /vehicles        -> 200 Get all vehicles
    GET    /vehicles/{id}   -> 200 Retrieve a vehicle (404 if missing)
    PATCH  /vehicles/{id}   -> 200 Update a vehicle   (404 if missing)
    DELETE /vehicles/{id}   -> 204 Delete a vehicle   (404 if missing)

Implemented with the Python standard library only (http.server), so it has
no third-party dependencies and runs anywhere Python 3.8+ is available.

Run:
    python app/server.py            # serves on http://localhost:8000
    python app/server.py --port 9000
"""

from __future__ import annotations

import argparse
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import count
from typing import Any, Dict, Optional

VEHICLE_FIELDS = ("nickName", "vin", "make", "model", "year", "miles")

_COLLECTION_RE = re.compile(r"^/vehicles/?$")
_ITEM_RE = re.compile(r"^/vehicles/(?P<id>[^/]+)/?$")


class VehicleStore:
    """Thread-safe in-memory vehicle store."""

    def __init__(self) -> None:
        self._data: Dict[int, Dict[str, Any]] = {}
        self._ids = count(1)
        self._lock = threading.Lock()

    def list(self):
        with self._lock:
            return list(self._data.values())

    def get(self, vid: int) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._data.get(vid)

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            vid = next(self._ids)
            record = {"id": vid}
            for field in VEHICLE_FIELDS:
                record[field] = payload.get(field)
            self._data[vid] = record
            return record

    def update(self, vid: int, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with self._lock:
            record = self._data.get(vid)
            if record is None:
                return None
            for field in VEHICLE_FIELDS:
                if field in payload:
                    record[field] = payload[field]
            return record

    def delete(self, vid: int) -> bool:
        with self._lock:
            return self._data.pop(vid, None) is not None


class VehicleHandler(BaseHTTPRequestHandler):
    store: VehicleStore = VehicleStore()
    server_version = "VehicleService/1.0"

    # -- helpers ----------------------------------------------------------

    def _send_json(self, status: int, body: Optional[Any]) -> None:
        payload = b"" if body is None else json.dumps(body).encode("utf-8")
        self.send_response(status)
        if payload:
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if payload:
            self.wfile.write(payload)

    def _read_json(self) -> Optional[Dict[str, Any]]:
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    @staticmethod
    def _parse_id(raw: str) -> Optional[int]:
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None

    def log_message(self, fmt: str, *args: Any) -> None:  # keep output tidy
        print(f"[server] {self.address_string()} - {fmt % args}")

    # -- routing ----------------------------------------------------------

    def do_GET(self) -> None:
        if _COLLECTION_RE.match(self.path):
            self._send_json(200, self.store.list())
            return
        m = _ITEM_RE.match(self.path)
        if m:
            self._get_one(m.group("id"))
            return
        self._send_json(404, {"message": "Not found"})

    def do_POST(self) -> None:
        if not _COLLECTION_RE.match(self.path):
            self._send_json(404, {"message": "Not found"})
            return
        payload = self._read_json()
        if payload is None:
            self._send_json(400, {"message": "Invalid JSON body"})
            return
        record = self.store.create(payload)
        self._send_json(201, record)

    def do_PATCH(self) -> None:
        m = _ITEM_RE.match(self.path)
        if not m:
            self._send_json(404, {"message": "Not found"})
            return
        vid = self._parse_id(m.group("id"))
        payload = self._read_json()
        if vid is None or payload is None:
            self._send_json(400, {"message": "Invalid request"})
            return
        record = self.store.update(vid, payload)
        if record is None:
            self._send_json(404, {"message": f"Vehicle {vid} not found"})
            return
        self._send_json(200, record)

    def do_DELETE(self) -> None:
        m = _ITEM_RE.match(self.path)
        if not m:
            self._send_json(404, {"message": "Not found"})
            return
        vid = self._parse_id(m.group("id"))
        if vid is None or not self.store.delete(vid):
            self._send_json(404, {"message": "Vehicle not found"})
            return
        self._send_json(204, None)

    def _get_one(self, raw_id: str) -> None:
        vid = self._parse_id(raw_id)
        record = self.store.get(vid) if vid is not None else None
        if record is None:
            self._send_json(404, {"message": f"Vehicle {raw_id} not found"})
            return
        self._send_json(200, record)


def build_server(host: str = "0.0.0.0", port: int = 8000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), VehicleHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Vehicle Service API server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    httpd = build_server(args.host, args.port)
    print(f"Vehicle Service listening on http://{args.host}:{args.port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.shutdown()


if __name__ == "__main__":
    main()
