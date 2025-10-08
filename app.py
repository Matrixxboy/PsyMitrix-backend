import os
from fastapi import FastAPI, Form, Depends
from Models import Question , ReportRequest as Report ,IntakeParameters
from fastapi.middleware.cors import CORSMiddleware
from aiModel import get_ai_response , generate_questions , generate_report
from Database.db import mycursor, mydb
from Database.dbHelper import save_question_to_db
from Database.dbTabels import create_tables
from typing import List , Dict , Any
from fastapi import HTTPException
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

@app.post("/questions/", response_model=Dict[str, Any])
def read_question(params: IntakeParameters):
    try:
        generated_questions_str = generate_questions(params)
        cleaned_str = generated_questions_str.strip()

        # 🧹 Clean up potential formatting (e.g., ```json ... ```)
        if cleaned_str.startswith("```json"):
            cleaned_str = cleaned_str.replace("```json", "").replace("```", "").strip()

        # 🧩 Parse JSON
        try:
            questions_data = json.loads(cleaned_str)
        except json.JSONDecodeError:
            print("⚠️ Invalid JSON detected. Attempting to fix...")
            # Attempt to auto-fix common JSON issues (like missing commas or quotes)
            cleaned_str = cleaned_str.replace("'", '"').replace("\n", "")
            try:
                questions_data = json.loads(cleaned_str)
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Malformed JSON returned by LLM.")

        # ✅ Validate final output structure
        if not isinstance(questions_data, dict) or len(questions_data) < 4:
            raise HTTPException(status_code=400, detail="Invalid question structure from AI response.")

        return {
            "message": "Questions generated successfully",
            "questions": questions_data
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"🚨 Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/")
def read_questions(question: Question):
    response = get_ai_response(question)
    return {
        "message": "Questions retrieved successfully",
        "question": {
        "question_type": question.question_type,
        "content": question.question,
        },
        "AI response": response
    }

@app.post("/report/")
def create_report(user: Report):
    report_raw = generate_report(user)

    # Ensure it's parsed JSON (not a string)
    try:
        report_data = json.loads(report_raw) if isinstance(report_raw, str) else report_raw
    except json.JSONDecodeError:
        report_data = {"error": "Invalid JSON format returned by AI."}

    return {
        "message": "Report generated successfully",
        "report": report_data
    }