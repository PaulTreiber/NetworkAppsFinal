"""Starter entry point for the REF620 Modbus client."""

from .config import RelayConfig
from .modbus import Ref620ModbusClient


def main() -> None:
    config = RelayConfig()
    client = Ref620ModbusClient(config)
    sample = client.read_holding_registers(address=2000, count=2)

    print("REF620 Modbus Client")
    print(f"Host: {config.host}:{config.port} (unit {config.unit_id})")
    print(f"Sample read @ 4X {sample.address}: {sample.raw_registers}")


if __name__ == "__main__":
    main()    
