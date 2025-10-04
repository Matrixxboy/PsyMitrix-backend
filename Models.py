from pydantic import BaseModel
from typing import Optional

class Question(BaseModel):
    question_type: str
    content: str
    answer: str
    answer_explanation: str


class User(BaseModel):
    username: str
    email: str
    password: str
    blood_group: Optional[str] = None
    birth_date: Optional[str] = None  # Format: 'YYYY-MM-DD'
    gender: Optional[str] = None