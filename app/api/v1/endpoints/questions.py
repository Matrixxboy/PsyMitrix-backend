import json
from fastapi import APIRouter
from app.schemas.models import IntakeParameters, questions
from app.services.ai_service import generate_questions
from app.utils.http_constants import HTTP_STATUS, HTTP_CODE
from app.utils.response_helper import make_response

router = APIRouter()

@router.post("/")
def read_question(params: IntakeParameters, questionList: questions):
    try:
        generated_questions_str = generate_questions(params, questionList).strip()

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
