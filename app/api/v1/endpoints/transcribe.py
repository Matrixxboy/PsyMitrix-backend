import os
from fastapi import APIRouter, UploadFile, Depends, File, HTTPException
from app.services.audio_service import transcribe_audio_content
from app.utils.http_constants import HTTP_STATUS, HTTP_CODE
from app.utils.response_helper import make_response

router = APIRouter()

def get_file(file: UploadFile = File(...)):
    return file

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = Depends(get_file)):
    try:
        # --- Validate file type ---
        SUPPORTED_FORMATS = {"mp3", "m4a", "wav", "flac","webm"}
        ext = os.path.splitext(file.filename)[1][1:].lower()
        if ext not in SUPPORTED_FORMATS:
            return make_response(
                HTTP_STATUS["BAD_REQUEST"],
                HTTP_CODE["VALIDATION"],
                "Unsupported file format",
                data={"supported_formats": SUPPORTED_FORMATS}
            )
        # --- Read file contents ---
        contents = await file.read()
        if not contents:
            return make_response(
                HTTP_STATUS["BAD_REQUEST"],
                HTTP_CODE["VALIDATION"],
                "Uploaded file is empty",
                data={"supported_formats": SUPPORTED_FORMATS}
            )
        
        # --- Call Service ---
        full_text = await transcribe_audio_content(contents, ext)

        # --- Return successful response ---
        return make_response(
            HTTP_STATUS["OK"],
            HTTP_CODE["OK"],
            message="Transcription successful",
            data={"text": full_text}
        )

    except HTTPException as http_err:
        return make_response("ERROR", http_err.status_code, http_err.detail)
    except Exception as e:
        return make_response(
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
            HTTP_CODE["ERROR"],
            message="An unexpected error occurred",
            data={"error": str(e)},
        )
