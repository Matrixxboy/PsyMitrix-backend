import os
from openai import OpenAI   # fixed import
from SystemPrompt import question_prompt ,report_prompt
from dotenv import load_dotenv
from Models.Models import IntakeParameters
load_dotenv()
from collections import defaultdict
from fastapi import HTTPException
from utils.response_helper import remove_backslashes 

def generate_questions(params: IntakeParameters) -> str:
    groq_api_key = os.getenv("GROQ_API")
    if not groq_api_key:
        raise ValueError("❌ GROQ_API environment variable not found.")

    data = {
        "Name": params.Name or "N/A",
        "Gender": params.Gender or "N/A",
        "DOB": params.DOB or "N/A",
        "Relationship_Status": params.Relationship_Status or "N/A",
        "Children": params.Children or "N/A",
        "Occupation": params.Occupation or "N/A",
        "Younger_Siblings": params.Younger_Siblings or "N/A",
        "Older_Siblings": params.Older_Siblings or "N/A",
        "Blood_Group": params.Blood_Group or "N/A",
    }

    # Escape all literal curly braces before formatting
    escaped_prompt = question_prompt.replace("{", "{{").replace("}", "}}")

    # Then reinsert only the placeholders we actually want to fill
    for key in data.keys():
        escaped_prompt = escaped_prompt.replace(f"{{{{{key}}}}}", f"{{{key}}}")

    safe_data = defaultdict(lambda: "N/A", data)
    dynamic_prompt = escaped_prompt.format_map(safe_data)

    try:
        client = OpenAI(
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1"
        )

        ai_response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an empathetic psychiatrist generating intake questions."},
                {"role": "user", "content": dynamic_prompt}
            ],
        )
        response_text = ai_response.choices[0].message.content
        return response_text

    except Exception as e:
        print(f"🚨 Error during LLM API call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def generate_report(params: IntakeParameters) -> str:
    groq_api_key = os.getenv("GROQ_API")
    if not groq_api_key:
        raise ValueError("❌ GROQ_API environment variable not found.")

    data = {
        "Name": params.Name or "N/A",
        "Gender": params.Gender or "N/A",
        "DOB": params.DOB or "N/A",
        "Relationship_Status": params.Relationship_Status or "N/A",
        "Children": params.Children or "N/A",
        "Occupation": params.Occupation or "N/A",
        "Younger_Siblings": params.Younger_Siblings or "N/A",
        "Older_Siblings": params.Older_Siblings or "N/A",
        "Blood_Group": params.Blood_Group or "N/A",
    }

    # Escape all literal curly braces before formatting
    escaped_prompt = report_prompt.replace("{", "{{").replace("}", "}}")

    # Then reinsert only the placeholders we actually want to fill
    for key in data.keys():
        escaped_prompt = escaped_prompt.replace(f"{{{{{key}}}}}", f"{{{key}}}")

    safe_data = defaultdict(lambda: "N/A", data)
    dynamic_prompt = escaped_prompt.format_map(safe_data)

    try:
        client = OpenAI(
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1"
        )

        ai_response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an empathetic psychiatrist generating intake questions."},
                {"role": "user", "content": dynamic_prompt}
            ],
        )
        response_text = ai_response.choices[0].message.content
        return response_text

    except Exception as e:
        print(f"🚨 Error during LLM API call: {e}")
        raise HTTPException(status_code=500, detail=str(e))
