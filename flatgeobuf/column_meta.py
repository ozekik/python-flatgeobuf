from dataclasses import dataclass
from typing import Optional

from flatgeobuf.FlatGeobuf.ColumnType import ColumnType


@dataclass
class ColumnMeta:
    name: str
    type: ColumnType
    title: Optional[str] = None
    description: Optional[str] = None
    width: int = 0
    precision: int = 0
    scale: int = 0
    nullable: bool = False
    unique: bool = False
    primary_key: bool = False
