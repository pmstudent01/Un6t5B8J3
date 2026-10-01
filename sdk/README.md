# Vehicle Service SDK (Python)

A lightweight Python client for the **Vehicle Service API**, derived from the
Postman *Vehicle Service Collection*.

## Install

```bash
pip install -e ./sdk
```

## Usage

```python
from vehicle_service_sdk import VehicleServiceClient, Vehicle

client = VehicleServiceClient(base_url="http://localhost:8000")

# Create
v = client.create_vehicle(Vehicle(
    nickName="The Lisa Marie",
    vin="4M2DV11W4RDJ53329",
    make="Mercury",
    model="Villager",
    year="1994",
    miles=159864,
))

# List
all_vehicles = client.list_vehicles()

# Retrieve
one = client.retrieve_vehicle(v.id)

# Update
updated = client.update_vehicle(v.id, {"miles": 159999})

# Delete
client.delete_vehicle(v.id)
```

## API surface

| SDK method | HTTP | Path |
|---|---|---|
| `create_vehicle(vehicle)` | POST | `/vehicles` |
| `list_vehicles()` | GET | `/vehicles` |
| `retrieve_vehicle(id)` | GET | `/vehicles/{id}` |
| `update_vehicle(id, changes)` | PATCH | `/vehicles/{id}` |
| `delete_vehicle(id)` | DELETE | `/vehicles/{id}` |
