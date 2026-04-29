"""Minimal Modbus TCP client wrapper."""

from dataclasses import dataclass

from .config import RelayConfig


@dataclass(slots=True)
class ReadResult:
    address: int
    count: int
    raw_registers: list[int]


class Ref620ModbusClient:
    """Small placeholder backend for future relay operations."""

    def __init__(self, config: RelayConfig) -> None:
        self.config = config

    def read_holding_registers(self, address: int, count: int = 1) -> ReadResult:
        """Return a stub result until live Modbus transport is implemented."""
        return ReadResult(address=address, count=count, raw_registers=[0] * count)
