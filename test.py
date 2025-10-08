import os
import json
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from typing import Dict, Any, Optional
from pydantic import BaseModel

# --- Pydantic Model for Request Body ---
class IntakeParameters(BaseModel):
    """
    Defines the structure for the patient's initial intake parameters 
    passed in the request body. All fields are optional.
    """
    Name: Optional[str] = None
    Gender: Optional[str] = None
    DOB: Optional[str] = None
    Relationship_Status: Optional[str] = None
    Children: Optional[int] = None
    Occupation: Optional[str] = None
    Younger_Siblings: Optional[int] = None
    Older_Siblings: Optional[int] = None

# --- FastAPI Application Setup ---
app = FastAPI(
    title="Psychological Intake Question Generator",
    description="An API endpoint that uses an LLM to generate structured psychiatric intake questions.",
)

# --- LLM Prompt Definition ---
# The prompt uses Python string formatting placeholders {Name}, {Gender}, etc., 
# which will be filled dynamically in the generate_questions function.
question_prompt = """
You are a highly skilled AI specializing in **Psychology and Behavioral Sciences**. Your persona is that of an experienced, non-judgemental psychiatrist conducting an initial, broad intake assessment.

**Task:**
Your goal is to generate **four distinct, open-ended questions** designed to gather initial, foundational information about a new individual's current life situation, support system, and general well-being. The questions must be framed as a psychiatrist would ask a new patient.

**Available Input Parameters (Use only to inform the *type* of question, not the content of the question itself):**
- Name : {Name}
- Gender : {Gender}
- DOB : {DOB}
- Relationship Status : {Relationship_Status}
- Children : {Children}
- Occupation : {Occupation}
- Younger Siblings : {Younger_Siblings}
- Older Siblings : {Older_Siblings}

**Output Format Instructions:**
Generate the response as a single, valid JSON object following this exact structure.
{
  "1": {"question": "...", "question_type": "current_status|support_system|wellbeing|history"},
  "2": {"question": "...", "question_type": "current_status|support_system|wellbeing|history"},
  "3": {"question": "...", "question_type": "current_status|support_system|wellbeing|history"},
  "4": {"question": "...", "question_type": "current_status|support_system|wellbeing|history"},
}
"""

# --- Core Logic to Interact with LLM ---

def generate_questions(params: IntakeParameters) -> str:
    """
    Calls the Groq API (using OpenAI client) to generate questions 
    and forces the response to be in JSON format, using dynamic parameters.
    """
    # NOTE: Ensure the GROQ_API environment variable is set
    groq_api_key = os.getenv("GROQ_API")
    if not groq_api_key:
        print("Error: GROQ_API environment variable not set.")
        raise ValueError("API Key for Groq not found in environment variables.")

    # Dynamically format the prompt using the received parameters
    dynamic_prompt = question_prompt.format(
        Name=params.Name or "N/A",
        Gender=params.Gender or "N/A",
        DOB=params.DOB or "N/A",
        Relationship_Status=params.Relationship_Status or "N/A",
        Children=params.Children if params.Children is not None else "N/A",
        Occupation=params.Occupation or "N/A",
        Younger_Siblings=params.Younger_Siblings if params.Younger_Siblings is not None else "N/A",
        Older_Siblings=params.Older_Siblings if params.Older_Siblings is not None else "N/A",
    )

    try:
        client = OpenAI(
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1"
        )

        ai_response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": dynamic_prompt, # Use the dynamically formatted prompt
                }
            ],
            model="mixtral-8x7b-32768", 
            response_format={"type": "json_object"}, 
        )

        response_text = ai_response.choices[0].message.content
        print(f"Raw LLM Response: {response_text[:100]}...")
        return response_text
        
    except Exception as e:
        print(f"Error during LLM API call: {e}")
        raise e

# --- FastAPI Endpoint ---

@app.post("/questions/", response_model=Dict[str, Any])
def read_question(params: IntakeParameters):
    """
    Endpoint to trigger the question generation using data from the request body.
    """
    try:
        # 1. Call the LLM and get the JSON string, passing the parameters
        generated_questions_str = generate_questions(params)
        
        # --- Robustly clean the string of markdown fences before parsing ---
        # This prevents common errors when the LLM wraps the JSON in ```json...
