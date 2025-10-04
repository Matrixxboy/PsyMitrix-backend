from pydantic import BaseModel

class Question(BaseModel):
    question_type: str
    content: str
    answer: str
    answer_explanation: str


class User(BaseModel):
    username: str
    email: str
    password: str
    blood_group: str = None
    birth_date: str = None  # Format: 'YYYY-MM-DD'
    gender: str = None