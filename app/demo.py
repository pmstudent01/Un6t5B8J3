"""End-to-end demo: drive the Vehicle Service API through the SDK.

This script starts the reference server in a background thread and then
exercises every endpoint using the generated ``vehicle_service_sdk``,
proving the SDK and the API implementation line up.

Run:
    python app/demo.py
"""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

# Make the SDK importable without installing it.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sdk"))

from vehicle_service_sdk import VehicleServiceClient, Vehicle  # noqa: E402
from server import build_server  # noqa: E402


def run_demo(base_url: str) -> None:
    client = VehicleServiceClient(base_url=base_url)

    print("1. Create a vehicle")
    created = client.create_vehicle(
        Vehicle(
            nickName="The Lisa Marie",
            vin="4M2DV11W4RDJ53329",
            make="Mercury",
            model="Villager",
            year="1994",
            miles=159864,
        )
    )
    print(f"   -> created id={created.id}, miles={created.miles}")

    print("2. List vehicles")
    vehicles = client.list_vehicles()
    print(f"   -> {len(vehicles)} vehicle(s)")

    print("3. Retrieve the vehicle")
    fetched = client.retrieve_vehicle(created.id)
    print(f"   -> {fetched.make} {fetched.model} ({fetched.year})")

    print("4. Update the vehicle (miles -> 159999)")
    updated = client.update_vehicle(created.id, {"miles": 159999})
    print(f"   -> miles now {updated.miles}")

    print("5. Delete the vehicle")
    client.delete_vehicle(created.id)
    print(f"   -> remaining vehicles: {len(client.list_vehicles())}")

    client.close()
    print("\nAll operations completed successfully.")


def main() -> None:
    host, port = "127.0.0.1", 8000
    httpd = build_server(host, port)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.3)  # let the server bind

    try:
        run_demo(f"http://{host}:{port}")
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
