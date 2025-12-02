from dataclasses import dataclass
from typing import Dict


@dataclass
class LogEntry:
    timestep: int
    evento: str
    detalhes: Dict[str, str]
