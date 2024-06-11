from dataclasses import dataclass
from typing import TypeAlias, Dict
from datetime import date


@dataclass
class Period:
    start: date
    end: date


MarkedDays: TypeAlias = Dict[date, str]
