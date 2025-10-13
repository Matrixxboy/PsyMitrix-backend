from pydantic import BaseModel
from typing import Literal , Optional , Any

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

class IntakeParameters(BaseModel):
    Name: Optional[str] = None
    Gender: Optional[str] = None
    DOB: Optional[str] = None
    Relationship_Status: Optional[str] = None
    Children: Optional[str] = None
    Occupation: Optional[str] = None
    Younger_Siblings: Optional[str] = None
    Older_Siblings: Optional[str] = None
    Blood_Group: Optional[str] = None

class ApiRespons(BaseModel):
    status_code: int
    code: str
    message: str
    data: Optional[Any] = None