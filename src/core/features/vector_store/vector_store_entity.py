from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class VectorEntity:
    file_id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    id: Optional[str] = None
