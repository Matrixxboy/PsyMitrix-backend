import json
from fastapi import APIRouter
from app.schemas.models import IntakeParameters, questions
from app.services.ai_service import generate_report
from app.services.pdf_service import generate_personality_pdf_safe
from app.utils.http_constants import HTTP_STATUS, HTTP_CODE
from app.utils.response_helper import make_response

router = APIRouter()

@router.post("/")
def create_report(params: IntakeParameters, questionList: questions):
    try:
        report_data = generate_report(params, questionList).strip()
        with open("new_response_data.json", "w") as f:
            json.dump(report_data, f)
        # If the model returned an error dict -> return error
        if isinstance(report_data, dict) and "error" in report_data:
            return make_response(
                HTTP_STATUS["INTERNAL_SERVER_ERROR"],
                HTTP_CODE["ERROR"],
                report_data["error"]
            )

        # ✓ Normalize output from AI model
        if isinstance(report_data, (dict, list)):
            report_cleaned = report_data
        else:
            try:
                report_cleaned = json.loads(report_data)
            except Exception:
                # If not valid JSON → fallback wrapper
                report_cleaned = {"report": str(report_data)}

        # ✓ Generate PDF File
        outname = f"{params.Name.replace(' ', '_')}_Personality_Report.pdf"
        reportFile = generate_personality_pdf_safe(
            filename=outname,
            data=report_cleaned,
            person_name=params.Name,
            generated_by="Endorphin AI"
        )

        # Safety log
        print(f"[OK] Generated PDF → {reportFile}")
        response_data = {
            "report_path": reportFile,
            "report_name": outname
            }
        # ✓ Return the generated PDF
        return make_response(
            status_code=HTTP_STATUS["OK"],
            code=HTTP_CODE["OK"],
            message="Report generated successfully",
            data=response_data
        )

    except Exception as e:
        return make_response(
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
            HTTP_CODE["ERROR"],
            str(e)
        )
