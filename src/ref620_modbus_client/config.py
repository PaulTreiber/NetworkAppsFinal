"""Configuration helpers for the REF620 Modbus client."""

from dataclasses import dataclass


@dataclass(slots=True)
class RelayConfig:
    host: str = "127.0.0.1"
    port: int = 502
    unit_id: int = 1
    timeout_seconds: float = 3.0
