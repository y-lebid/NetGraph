from dataclasses import asdict, dataclass
from typing import Optional


@dataclass(frozen=True)
class Device:

    ip: str
    mac: Optional[str] = None
    name: Optional[str] = None
    device_type: str = "unknown"

    @classmethod
    def from_dict(cls, value):
        return cls(
            ip=str(value["ip"]),
            mac=value.get("mac"),
            name=value.get("name"),
            device_type=value.get("device_type", "unknown"),
        )

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class Connection:

    source: str
    destination: str
    weight: float = 1

    def to_dict(self):
        return asdict(self)
