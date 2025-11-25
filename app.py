import io
import os
import json
from toon import encode
from pydub import AudioSegment
import speech_recognition as sr
from fastapi import FastAPI , Request, FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from Models.Models import IntakeParameters ,userQustions
from AI.aiModel import  generate_questions, generate_report , generate_report_from_questions
AudioSegment.ffprobe   = "E:\\ffmpeg\\bin\\ffprobe.exe"
AudioSegment.converter = "E:\\ffmpeg\\bin\\ffmpeg.exe"
from utils.http_constants import HTTP_STATUS, HTTP_CODE
from utils.response_helper import make_response
from generate_pdf import generate_personality_pdf

# from fastapi.responses import JSONResponse
# from Helper.helperFunctions import audio_to_text_online

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

@app.post("/questions_report")
async def question_report(params: userQustions):
    try:
        if params is None:
            return make_response(
                status_code=HTTP_STATUS["BAD_REQUEST"],
                code=HTTP_CODE["BAD_REQUEST"],
                message="No questions are embedded",
                data={}
            )

        questions = f"{encode(params.questions)}"
        report_data_string = ""

        if params.take and params.take == "0":
            report_data_string, _, _, _ = generate_report_from_questions(questions=questions)
        else:
            return make_response(
                status_code=HTTP_STATUS["BAD_REQUEST"],
                code=HTTP_CODE["BAD_REQUEST"],
                message="Cant Generate report now",
                data={}
            )

        # STEP 2: Clean and parse the JSON data from the AI model
        if report_data_string.startswith("```json"):
            report_data_string = (
                report_data_string
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        try:
            report_data_dict = json.loads(report_data_string)
        except json.JSONDecodeError:
            return make_response(
                HTTP_STATUS["INTERNAL_SERVER_ERROR"],
                HTTP_CODE["ERROR"],
                "Malformed JSON data received from AI model, cannot generate PDF."
            )

        # STEP 3: Generate the PDF
        pdf_filename = f"{params.name.replace(' ', '_')}_Personality_Report.pdf"
        generate_personality_pdf(
            filename=pdf_filename,
            data=report_data_dict,
            person_name=params.name,
            generated_by=params.generated_by
        )

        # STEP 4: Return the generated file
        return FileResponse(
            path=pdf_filename,
            filename=pdf_filename,
            media_type="application/pdf"
        )

    except Exception as e:
        print(f"ERROR in /questions_report: {e}")  # Added for debugging
        return make_response(
            status_code=HTTP_STATUS["INTERNAL_SERVER_ERROR"],
            code=HTTP_CODE["INTERNAL_SERVER_ERROR"],
            message=f"An unexpected error occurred: {str(e)}",
            data={}
        )
    
@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
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
        # --- Load and convert to WAV in memory ---
        audio_segment = AudioSegment.from_file(io.BytesIO(contents), format=ext)
        wav_buffer = io.BytesIO()
        audio_segment.export(wav_buffer, format="wav")
        wav_buffer.seek(0)

        # --- Speech recognition in chunks ---
        recognizer = sr.Recognizer()
        full_text = ""

        with sr.AudioFile(wav_buffer) as source:
            while True:
                try:
                    audio_data = recognizer.record(source, duration=30)
                    if not audio_data.frame_data:
                        break
                    text = recognizer.recognize_google(audio_data)
                    full_text += " " + text
                except Exception as e:
                    return make_response(
                        HTTP_STATUS["INTERNAL_SERVER_ERROR"],
                        HTTP_CODE["ERROR"],
                        message="Error during transcription",
                        data={"error": str(e)}
                    )

        # --- Return successful response ---
        return make_response(
            HTTP_STATUS["OK"],
            HTTP_CODE["OK"],
            message="Transcription successful",
            data={"text": full_text.strip()}
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
