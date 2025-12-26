from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class VectorEntity:
    file_id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    id: Optional[str] = None
