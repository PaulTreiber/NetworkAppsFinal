"""Manual Modbus test reads for REF620 points from the ABB point-list manual."""

from .config import RelayConfig
from .modbus import PointReading, Ref620ModbusClient
from .points import TEST_POINT_GROUPS


def main() -> None:
    config = RelayConfig()
    client = Ref620ModbusClient(config)

    print("REF620 Modbus Test Reads")
    print(f"Host: {config.host}:{config.port} (unit {config.unit_id})")
    print()

    for group_name, points in TEST_POINT_GROUPS.items():
        print(f"[{group_name}]")
        for point in points:
            try:
                reading = client.read_point(point)
            except Exception as exc:
                print(f"FAIL {point.address:<5} {point.name}: {exc}")
                continue
            print(_format_reading(reading))
        print()


def _format_reading(reading: PointReading) -> str:
    point = reading.point
    unit_suffix = f" {point.unit}" if point.unit else ""
    bit_suffix = f":{point.bit}" if point.bit is not None else ""
    label = point.label or point.name
    return (
        f"OK   {point.address}{bit_suffix:<5} "
        f"{label}: {reading.value:g}{unit_suffix} "
        f"raw={reading.raw_registers} source={point.source}"
    )


if __name__ == "__main__":
    main()
