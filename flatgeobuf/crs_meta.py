from dataclasses import dataclass
from typing import Optional

@dataclass
class CrsMeta:
    org: Optional[str] = None
    code: int = 0
    name: Optional[str] = None
    description: Optional[str] = None
    wkt: Optional[str] = None
    code_string: Optional[str] = None