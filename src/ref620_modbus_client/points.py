"""Point metadata models."""

from dataclasses import dataclass


@dataclass(slots=True)
class PointDefinition:
    name: str
    address: int
    register_count: int = 1
    description: str = ""
    scale_factor: float = 1.0
    offset: float = 0.0
