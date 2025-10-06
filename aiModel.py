import os
import json
import requests
from openai import OpenAI   # fixed import
from SystemPrompt import system_prompt , question_prompt ,report_prompt
from dotenv import load_dotenv
from Models import User, Question , ReportRequest as Report
load_dotenv()

from Database.db import mycursor, mydb
from typing import List


def get_ai_response(question):
    """
    question: a dict with keys 'question_type', 'content', 'answer', 'answer_explanation'
    """
    data = {
        "question_type": question.question_type,
        "content": question.content,
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


def generate_questions():
    prompt = question_prompt
    client = OpenAI(
        api_key=os.getenv("GROQ_API"),
        base_url="https://api.groq.com/openai/v1"
    )

    ai_response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="openai/gpt-oss-20b",
    )

    # Safely extract text openai/gpt-oss-20b
    try:
        response_text = ai_response.choices[0].message.content
        return response_text
    except (IndexError, AttributeError, KeyError, json.JSONDecodeError):
        return {"error": "Unexpected response format"}


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

