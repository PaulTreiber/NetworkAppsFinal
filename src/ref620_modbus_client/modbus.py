"""Minimal Modbus TCP client wrapper."""

from dataclasses import dataclass

from pymodbus.client import ModbusTcpClient

from .config import RelayConfig
from .points import PointDefinition


@dataclass
class ReadResult:
    address: int
    count: int
    raw_registers: list[int]


@dataclass
class PointReading:
    point: PointDefinition
    raw_registers: list[int]
    value: float


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

    def write_holding_register(self, address: int, value: int) -> None:
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
            result = client.write_register(
                address=address,
                value=value,
                slave=self.config.unit_id,
            )

            if result.isError():
                raise RuntimeError(f"Modbus write failed: {result}")
        finally:
            client.close()

    def read_point(self, point: PointDefinition) -> PointReading:
        result = self.read_holding_registers(
            address=point.address,
            count=point.register_count,
        )
        return PointReading(
            point=point,
            raw_registers=result.raw_registers,
            value=decode_registers(point, result.raw_registers),
        )

    def read_points(self, points: list[PointDefinition]) -> list[PointReading]:
        return [self.read_point(point) for point in points]


def decode_registers(point: PointDefinition, registers: list[int]) -> float:
    if len(registers) != point.register_count:
        raise ValueError(
            f"{point.name} expected {point.register_count} registers, got {len(registers)}"
        )

    if point.data_type == "u16":
        raw_value = registers[0]
    elif point.data_type == "s16":
        raw_value = _to_signed(registers[0], bits=16)
    elif point.data_type == "bit":
        if point.bit is None:
            raise ValueError(f"{point.name} is a bit point with no bit number")
        raw_value = (registers[0] >> point.bit) & 1
    elif point.data_type == "u32":
        raw_value = _combine_u32(registers)
    elif point.data_type == "s32":
        raw_value = _to_signed(_combine_u32(registers), bits=32)
    else:
        raise ValueError(f"Unsupported data type for {point.name}: {point.data_type}")

    return (raw_value / point.scale_factor) + point.offset


def _combine_u32(registers: list[int]) -> int:
    high_word, low_word = registers
    return (high_word << 16) | low_word


def _to_signed(value: int, bits: int) -> int:
    sign_bit = 1 << (bits - 1)
    return value - (1 << bits) if value & sign_bit else value
