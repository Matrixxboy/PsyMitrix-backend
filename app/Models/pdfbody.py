from pydantic import BaseModel
from typing import List, Optional, Dict

class PdfBody(BaseModel):
    sections: List[str]
    templateId: Optional[int] = 0
    parameters: Optional[Dict] = {}
