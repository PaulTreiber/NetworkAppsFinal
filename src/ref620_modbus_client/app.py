"""Entry point for collecting REF620 Modbus measurements."""

import csv
from datetime import datetime, timezone
from pathlib import Path

from .config import RelayConfig
from .modbus import PointReading, Ref620ModbusClient
from .points import DEFAULT_POINTS


def main() -> None:
    config = RelayConfig()
    client = Ref620ModbusClient(config)
    readings = client.read_points(DEFAULT_POINTS)

    print("REF620 Modbus Client")
    print(f"Host: {config.host}:{config.port} (unit {config.unit_id})")

    timestamp = datetime.now(timezone.utc).isoformat()
    for reading in readings:
        unit_suffix = f" {reading.point.unit}" if reading.point.unit else ""
        label = reading.point.label or reading.point.name
        print(
            f"{label}: {reading.value:g}{unit_suffix} "
            f"raw={reading.raw_registers}"
        )

    append_csv_row(config.csv_path, timestamp, readings)
    print(f"Saved readings to {config.csv_path}")


def append_csv_row(
    csv_path: str,
    timestamp: str,
    readings: list[PointReading],
) -> None:
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()

    fieldnames = ["timestamp_utc"] + [reading.point.name for reading in readings]

    with path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        row = {"timestamp_utc": timestamp}
        row.update({reading.point.name: reading.value for reading in readings})
        writer.writerow(row)


if __name__ == "__main__":
    main()
