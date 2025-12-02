<<<<<<< HEAD
from dataclasses import dataclass
from typing import Dict


@dataclass
class LogEntry:
    timestep: int
    evento: str
    detalhes: Dict[str, str]
=======
import logging

logging.basicConfig(
    filename="simulacao.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def registrar(msg):
    logging.info(msg)
>>>>>>> 22c94c5cea82f2b8a00cc4ee03d8a5dcc284771b
