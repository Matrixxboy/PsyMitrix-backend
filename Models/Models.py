from pydantic import BaseModel
from typing import Optional , Any

class Question(BaseModel):
    question: str
    question_type: str
    answer:str
    options: list[str] = None

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

class questions(BaseModel):
    questions: list[Question] = []
    take:str = None
    name:str = None
    generated_by:str = None

class ApiRespons(BaseModel):
    status_code: int
    code: str
    message: str
    data: Optional[Any] = None

class userQustions(BaseModel):
    take:str
    questions:dict
    name:str
    generated_by:str

