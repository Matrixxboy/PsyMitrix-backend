from pydantic import BaseModel
from typing import Literal

class Question(BaseModel):
    question: str
    question_type: str


class User(BaseModel):
    username: str
    email: str
    password: str
    blood_group: str = None
    birth_date: str = None  # Format: 'YYYY-MM-DD'
    gender: str = None

class ReportRequest(BaseModel):
    name: str
    gender: Literal['Male', 'Female', 'Other']
    dob: str
    blood_group: str
    older_siblings: int
    younger_siblings: int