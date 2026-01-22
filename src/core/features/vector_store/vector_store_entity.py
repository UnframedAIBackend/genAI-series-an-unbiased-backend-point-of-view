from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class VectorEntity:
    file_id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
