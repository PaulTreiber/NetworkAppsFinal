"""Configuration helpers for the REF620 Modbus client."""

from dataclasses import dataclass


@dataclass
class RelayConfig:
    host: str = "192.168.219.50"
    port: int = 502
    unit_id: int = 1
    timeout_seconds: float = 3.0
