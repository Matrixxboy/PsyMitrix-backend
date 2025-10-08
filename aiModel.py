import os
import json
import requests
from openai import OpenAI   # fixed import
from SystemPrompt import system_prompt , question_prompt ,report_prompt
from dotenv import load_dotenv
from Models import User, Question , ReportRequest as Report , IntakeParameters
load_dotenv()
from collections import defaultdict
from Database.db import mycursor, mydb
from typing import List
from fastapi import HTTPException

def get_ai_response(question):
    """
    question: a dict with keys 'question_type', 'content', 'answer', 'answer_explanation'
    """
    data = {
        "question_type": question.question_type,
        "content": question.question,
        "answer": question.answer,
        "answer_explanation_type": question.answer_explanation,
    }

    # Build the prompt string
    prompt = f"{system_prompt}\nAnswer the following question:\n" \
             f"Content: {data['content']}\n" \
             f"Question Type: {data['question_type']}\n" \
             f"Answer: {data['answer']}\n" \
             f"Answer Explanation length: {data['answer_explanation_type']}\n" \
             "You just have to give the very short answer and have to find the symptoms for the mental health condition."


    # Initialize OpenAI client
    client = OpenAI(
        api_key=os.getenv("GROQ_API"),   # GROQ API key
        base_url="https://api.groq.com/openai/v1"  # fixed parameter name
    )

    # Create a response
    ai_response = client.responses.create(
        model="openai/gpt-oss-20b",
        input=prompt
    )
    try:
        response = ai_response.output[1].content[0].text.strip()
        try:
            # Try to parse JSON if it’s valid
            response_json = json.loads(response)
            return response_json
        except json.JSONDecodeError:
            # If not JSON, just return text
            return response
    except (IndexError, AttributeError, KeyError):
        response = "Error: Unable to retrieve response"

    return response


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
        print(f"✅ Raw LLM Response (first 200 chars): {response_text[:200]}...")
        return response_text

    except Exception as e:
        print(f"🚨 Error during LLM API call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def generate_report(user: Report):
    prompt = report_prompt.format(
        Name=user.name,
        Gender=user.gender,
        DOB=user.dob,
        Blood_Group=user.blood_group,
        Older_Siblings=user.older_siblings,
        Younger_Siblings=user.younger_siblings
    )

    client = OpenAI(
        api_key=os.getenv("GROQ_API"),
        base_url="https://api.groq.com/openai/v1"
    )

    try:
        ai_response = client.chat.completions.create(
            model="openai/gpt-oss-20b",  # ✅ or another Groq-supported model
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the text safely
        response_text = ai_response.choices[0].message.content.strip()
        return response_text

    except Exception as e:
        print(f"⚠️ Error generating report: {e}")
        return "Error: Unable to generate report due to unexpected response format."

