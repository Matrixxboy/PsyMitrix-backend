import json
import os
import io
import requests
from fastapi import APIRouter 
from fastapi.responses import StreamingResponse
from app.utils.http_constants import HTTP_STATUS, HTTP_CODE
from app.utils.response_helper import make_response
from app.Models.users import User
from app.Models.pdfbody import PdfBody
from dotenv import load_dotenv
load_dotenv()

router=APIRouter(prefix="/assessments")

CLIENT_ID = os.getenv("PSY_ENDRO_CLIENT_ID")
CLIENT_SECRET = os.getenv("PSY_ENDRO_CLIENT_SECRET_KEY")

#1. Get available assessments list
@router.get("/list")
def get_assessments():
    try:
        psypack_url = "https://asia-south1-psypack-deploy.cloudfunctions.net/api/get-assessments"
        headers = {
            "clientId": CLIENT_ID,
            "clientSecret": CLIENT_SECRET
        }
        response = requests.get(psypack_url, headers=headers)
        data = response.json()
        assessments = data.get("assessments", [])
        return make_response(
            HTTP_STATUS["OK"],
            HTTP_CODE["OK"],
            message="Assessments fetched successfully",
            data=assessments
        )
    except Exception as e:
        return make_response(
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
            HTTP_CODE["INTERNAL_SERVER_ERROR"],
            message=str(e),
            data={}
        )

#2. Initiate assessment
@router.post("/initiate")
def initiate_assessment(assessment_id: str,user: User):
    try:
        psypack_url = "https://asia-south1-psypack-deploy.cloudfunctions.net/api/initiate-assessment"
        headers = {
            "clientId": CLIENT_ID,
            "clientSecret": CLIENT_SECRET,
            "Content-Type": "application/json"
        }
        body ={
            "assessmentId": assessment_id,
            "emailList" : [user.email],
            "settings":{
                "emailAssessment": True,
                "clientAccess" : True,
                "practitionerDashboardAccess": True,
                "practitionerApiAccess": True,
            },
            "redirectUrl": "psypack.com",
            "initiationType": 2
        }
        response = requests.post(psypack_url, headers=headers, json=body)
        data = response.json()
        return make_response(
            HTTP_STATUS["OK"],
            HTTP_CODE["OK"],
            message="Assessment initiated successfully",
            data=data
        )
    except Exception as e:
        return make_response(
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
            HTTP_CODE["INTERNAL_SERVER_ERROR"],
            message=str(e),
            data={}
        )



#3. Get assessment status
@router.get("/status/")
def get_assessment_status(user_assessment_id: str):
    try:
        headers = {
            "clientId": CLIENT_ID,
            "clientSecret": CLIENT_SECRET
        }
        psypack_url = f"https://asia-south1-psypack-deploy.cloudfunctions.net/api/assessment-status/{user_assessment_id}"
        response = requests.get(psypack_url, headers=headers)
        data = response.json()
        return make_response(
            HTTP_STATUS["OK"],
            HTTP_CODE["OK"],
            message="Assessment status fetched successfully",
            data=data
        )
    except Exception as e:
        return make_response(
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
            HTTP_CODE["INTERNAL_SERVER_ERROR"],
            message=str(e),
            data={}
        )


#4. Get report PDF  
@router.post("/generate-report")
def generate_report(report_id: str, body: PdfBody):
    """
    Fetch PsyPack PDF report and return as downloadable PDF.
    """

    try:
        url = f"https://asia-south1-psypack-deploy.cloudfunctions.net/api/report/{report_id}/pdf"

        headers = {
            "clientid": CLIENT_ID,
            "clientsecret": CLIENT_SECRET,
            "Content-Type": "application/json"
        }

        payload = {
            "sections": body.sections,
            "templateId": body.templateId or 0,
            "parameters": body.parameters or {}
        }

        # Send request to PsyPack
        response = requests.post(url, headers=headers, json=payload)

        # If PsyPack returns an error
        if response.status_code != 200:
            return {
                "status": "error",
                "message": response.text,
                "http_code": response.status_code
            }

        # Convert PDF bytes to stream
        pdf_stream = io.BytesIO(response.content)

        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=psypack_report.pdf"}
        )

    except Exception as e:
        return {"error": str(e)}