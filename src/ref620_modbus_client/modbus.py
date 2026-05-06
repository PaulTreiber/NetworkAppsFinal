"""Minimal Modbus TCP client wrapper."""

from dataclasses import dataclass

from pymodbus.client import ModbusTcpClient

from .config import RelayConfig


@dataclass
class ReadResult:
    address: int
    count: int
    raw_registers: list[int]


class Ref620ModbusClient:
    """Small Modbus TCP client for reading relay registers."""

    def __init__(self, config: RelayConfig) -> None:
        self.config = config

    def read_holding_registers(self, address: int, count: int = 1) -> ReadResult:
        client = ModbusTcpClient(
            self.config.host,
            port=self.config.port,
            timeout=self.config.timeout_seconds,
        )

        if not client.connect():
            raise RuntimeError(
                f"Could not connect to {self.config.host}:{self.config.port}"
            )

        try:
            result = client.read_holding_registers(
                address=address,
                count=count,
                slave=self.config.unit_id,
            )

            if result.isError():
                raise RuntimeError(f"Modbus read failed: {result}")

            return ReadResult(
                address=address,
                count=count,
                raw_registers=list(result.registers),
            )
        finally:
            client.close()
