from pydantic import BaseModel

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