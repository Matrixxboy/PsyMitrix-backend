import os
from fastapi import FastAPI, Form, Depends
from Models import Question , User
from fastapi.middleware.cors import CORSMiddleware
from aiModel import get_ai_response , generate_questions
from dbHelper import save_question_to_db
from db import mycursor, mydb
from dbTabels import create_tables, create_user_details_table
from typing import List
import json

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
    try:
        # Step 1: Create tables (if not exist)
        create_tables()

        # Step 2: Generate questions
        generated_questions = generate_questions()
        generated_questions = json.loads(generated_questions)
        print("Generated Questions:", generated_questions)
       
        # Step 3: Save generated questions to DB
        for content, question_data in generated_questions.items():
            print("Saving question:", question_data)  # Debugging line
            save_question_to_db(content,question_data, mydb, mycursor)

        # Step 4: Return combined response
        return {
            "message": "Questions generated and saved successfully",
            "generated_questions": generated_questions,
        }

    except Exception as e:
        return {"error": f"Failed to process questions: {str(e)}"}
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()
            print("MySQL connection is closed")

@app.post("/analyze/")
def read_questions(question: Question):
    response = get_ai_response(question)
    return {
        "message": "Questions retrieved successfully",
        "question": {
        "question_type": question.question_type,
        "content": question.content,
        },
        "AI response": response
    }