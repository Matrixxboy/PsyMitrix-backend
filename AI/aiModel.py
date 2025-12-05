import os
import json
from openai import OpenAI   # fixed import
from SystemPrompt import question_prompt ,report_prompt , questio_report_prompt
from dotenv import load_dotenv
from Models.Models import IntakeParameters , questions
load_dotenv()
from collections import defaultdict
from fastapi import HTTPException
from utils.response_helper import remove_backslashes
from toon import encode


OPEN_AI_API_KEY = os.getenv("OPEN_AI_API")
if not OPEN_AI_API_KEY:
    raise ValueError("❌ OPEN_AI_API environment variable not found.")


def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)
        start = end - overlap  # sliding window overlap

    return chunks


def generate_questions(params: IntakeParameters , questionList : questions) -> str:
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

    # Format previous questions and answers
    formatted_questions = []
    if questionList.questions:
        for idx, q in enumerate(questionList.questions, 1):
            formatted_questions.append(f"Q{idx}: {q.question}\nA{idx}: {q.answer}")
    
    questions_str = "\n".join(formatted_questions)

    # Escape all literal curly braces before formatting
    escaped_prompt = question_prompt.replace("{", "{{").replace("}", "}}")

    # Then reinsert only the placeholders we actually want to fill
    for key in data.keys():
        escaped_prompt = escaped_prompt.replace(f"{{{{{key}}}}}", f"{{{key}}}")
    
    # Prepare {questions} for format_map
    escaped_prompt = escaped_prompt.replace("{{questions}}", "{questions}")

    safe_data = defaultdict(lambda: "N/A", data)
    safe_data["questions"] = questions_str
    dynamic_prompt = escaped_prompt.format_map(safe_data)

    try:
        client = OpenAI(api_key=OPEN_AI_API_KEY)

        ai_response = client.chat.completions.create(
            model="gpt-4.1",   # or "gpt-4.1-mini" / "gpt-4.1-large"
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


def generate_report(params: IntakeParameters , questionList : questions) -> str:
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
    # Format previous questions and answers
    formatted_questions = []
    if questionList.questions:
        for idx, q in enumerate(questionList.questions, 1):
            formatted_questions.append(f"Q{idx}: {q.question}\nA{idx}: {q.answer}")
    
    questions_str = "\n".join(formatted_questions)
    data["questionList"] = questions_str
    print("\n\nQuestion List for Report Generation:")
    print(questions_str)
    # Escape all literal curly braces before formatting
    escaped_prompt = report_prompt.replace("{", "{{").replace("}", "}}")

    # Then reinsert only the placeholders we actually want to fill
    for key in data.keys():
        escaped_prompt = escaped_prompt.replace(f"{{{{{key}}}}}", f"{{{key}}}")

    safe_data = defaultdict(lambda: "N/A", data)
    dynamic_prompt = escaped_prompt.format_map(safe_data)
    print("Dynamic Prompt for Report Generation:")
    print(dynamic_prompt)
    try:
        client = OpenAI(api_key=OPEN_AI_API_KEY)

        ai_response = client.chat.completions.create(
            model="gpt-4.1",   # or "gpt-4.1-mini" / "gpt-4.1-large"
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


def generate_report_from_questions(questions: str) -> str:
    try:
        # Prepare prompt template safely
        base_prompt = remove_backslashes(questio_report_prompt)
        base_prompt = base_prompt.replace("{", "{{").replace("}", "}}")
        # Chunk the prompt (NOT questions)
        chunks = chunk_text(questions, chunk_size=200, overlap=20)

        # Inject only the first few chunks into prompt to reduce tokens
        chunk_context = "\n\n".join(chunks[:3])
        dynamic_prompt = base_prompt.format(questions=chunk_context)

        # Call OpenAI API
        client = OpenAI(api_key=OPEN_AI_API_KEY)

        ai_response = client.chat.completions.create(
            model="gpt-4.1",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an empathetic psychiatrist generating an intake analysis report."},
                {"role": "user", "content": dynamic_prompt}
            ],
        )

        llm_output = ai_response.choices[0].message.content

        # Remove code fences if the model added them accidentally
        cleaned_output = (
            llm_output.replace("```json", "")
                      .replace("```", "")
                      .strip()
        )
        input_tokens = f"{ai_response.usage.prompt_tokens}"
        output_tokens = f"{ai_response.usage.completion_tokens}"
        total_tokens = f"{ai_response.usage.total_tokens}"

        print("question_report_data.json saved successfully.")
        return cleaned_output, input_tokens, output_tokens , total_tokens


    except Exception as e:
        print(f"🚨 Error during LLM API call: {e}")
        raise HTTPException(status_code=500, detail=str(e))
