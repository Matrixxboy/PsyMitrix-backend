import os
import json
from fastapi import FastAPI , Request
# from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from Models.Models import IntakeParameters
from AI.aiModel import  generate_questions, generate_report
# from Database.db import mycursor, mydb
# from Database.dbHelper import save_question_to_db
# from Database.dbTabels import create_tables

from utils.http_constants import HTTP_STATUS, HTTP_CODE
from utils.response_helper import make_response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Convert FastAPI’s validation error into your standard structure
    error_messages = []
    print(request)
    for err in exc.errors():
        loc = " -> ".join(map(str, err.get("loc", [])))
        msg = err.get("msg", "")
        error_messages.append(f"{loc}: {msg}")

    return make_response(
        HTTP_STATUS["BAD_REQUEST"],
        HTTP_CODE["VALIDATION"],
        "Validation error",
        {"errors": error_messages}
    )

@app.get("/")
def read_root():
    return make_response(
        HTTP_STATUS["OK"],
        HTTP_CODE["OK"],
        "Server is running 🚀",
        {"hello": "world"}
    )

@app.post("/questions/")
def read_question(params: IntakeParameters):
    try:
        generated_questions_str = generate_questions(params).strip()

        if generated_questions_str.startswith("```json"):
            generated_questions_str = generated_questions_str.replace("```json", "").replace("```", "").strip()

        try:
            questions_data = json.loads(generated_questions_str)
        except json.JSONDecodeError:
            generated_questions_str = generated_questions_str.replace("'", '"').replace("\n", "")
            try:
                questions_data = json.loads(generated_questions_str)
            except json.JSONDecodeError:
                return make_response(
                    HTTP_STATUS["INTERNAL_SERVER_ERROR"],
                    HTTP_CODE["ERROR"],
                    "Malformed JSON returned by AI model."
                )

        if not isinstance(questions_data, dict) or len(questions_data) < 3:
            return make_response(
                HTTP_STATUS["BAD_REQUEST"],
                HTTP_CODE["VALIDATION"],
                "Invalid question structure from AI response."
            )

        return make_response(
            HTTP_STATUS["OK"],
            HTTP_CODE["OK"],
            "Questions generated successfully",
            questions_data
        )

    except Exception as e:
        print(f"🚨 Unexpected Error: {e}")
        return make_response(
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
            HTTP_CODE["ERROR"],
            str(e)
        )

@app.post("/report/")
def create_report(user: IntakeParameters):
    try:
        report_data = generate_report(user)

        # If the model returned an error structure, bubble it up
        if isinstance(report_data, dict) and "error" in report_data:
            return make_response(
                HTTP_STATUS["INTERNAL_SERVER_ERROR"],
                HTTP_CODE["ERROR"],
                report_data["error"]
            )

        # Ensure we return JSON-serializable data.
        # If the model returned a dict/list already, use it as-is;
        # if it returned a JSON string, try to parse it; otherwise wrap it.
        if isinstance(report_data, (dict, list)):
            report_cleaned = report_data
        else:
            try:
                report_cleaned = json.loads(report_data)
            except Exception:
                report_cleaned = {"report": str(report_data)}

        return make_response(
            HTTP_STATUS["OK"],
            HTTP_CODE["OK"],
            "Report generated successfully",
            data=report_cleaned
        )
    except Exception as e:
        return make_response(
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
            HTTP_CODE["ERROR"],
            str(e)
        )
