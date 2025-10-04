import os
from fastapi import FastAPI, Form, Depends
from Models import Question , User
from fastapi.middleware.cors import CORSMiddleware
from aiModel import get_ai_response , generate_questions , save_question_to_db , create_user_in_db
from db import mycursor, mydb
from dbTabels import create_tables, create_user_details_table
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/questions/")
def read_question():
    response = generate_questions()
    return response

@app.post("/analyze/")
def read_questions(question: Question):
    response = get_ai_response(question)
    return {
        "message": "Questions retrieved successfully",
        "question": {
        "question_type": question.question_type,
        "content": question.content,
        "answer": question.answer,
        "answer_explanation": question.answer_explanation,
        },
        "AI response": response
    }

@app.post("/save/")
def save_question(question: List[Question]):
    try:
        create_tables()
        response = save_question_to_db(question)
        success_mg = "Question saved successfully"
        if response.get("message") == success_mg:
            mycursor.execute("SELECT * FROM questions")
            all_questions = mycursor.fetchall()
            response["all_questions"] = all_questions
    except Exception as e:
        return {"error": f"Failed to create tables: {str(e)}"}

    return response


@app.post("/user/create/")
def create_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    blood_group: str = Form(None),
    birth_date: str = Form(None),
    gender: str = Form(None),
):
    create_user_details_table()
    user = User(
        username=username,
        email=email,
        password=password,
        blood_group=blood_group,
        birth_date=birth_date,
        gender=gender,
    )
    response = create_user_in_db(user=user, mydb=mydb, mycursor=mycursor)
    return response