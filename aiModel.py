import os
import json
import requests
from openai import OpenAI   # fixed import
from SystemPrompt import system_prompt , question_prompt
from dotenv import load_dotenv
from Models import User
load_dotenv()

from db import mycursor, mydb
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

    ai_response = client.responses.create(
        model="openai/gpt-oss-20b",
        input=prompt
    )

    # Safely extract text
    try:
        response_text = ai_response.output[1].content[0].text.strip()

        # Try to parse JSON if it’s valid
        try:
            response_json = json.loads(response_text)
            return response_json
        except json.JSONDecodeError:
            # If not JSON, just return text
            return [response_text]

    except (IndexError, AttributeError, KeyError):
        return {"error": "Unexpected response format"}


def save_question_to_db(questions):
    try:
        connection = mydb
        cursor = mycursor

        if connection.is_connected():
            insert_query = """
            INSERT INTO questions (content, question_type, answer, answer_explanation)
            VALUES (%s, %s, %s, %s)
            """
            # Loop through each Question object
            for question in questions:
                record = (
                    question.content,
                    question.question_type,
                    question.answer,
                    question.answer_explanation
                )
                cursor.execute(insert_query, record)

            connection.commit()
            return {"message": f"{len(questions)} question(s) saved successfully!"}

    except Exception as e:
        return {"error": f"Error: {e}"}

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def create_user_in_db(user: User, mydb, mycursor):
    try:
        if mydb.is_connected():
            insert_query = """
            INSERT INTO users (username, email, password_hash, blood_group, birth_date, gender)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            # Use password as-is for now; consider hashing in production!
            record = (
                user.username,
                user.email,
                user.password,          # Replace with hashed password in production
                user.blood_group,
                user.birth_date,        # Ensure it's a string in 'YYYY-MM-DD' format
                user.gender
            )
            mycursor.execute(insert_query, record)
            mydb.commit()
            return {"message": "User created successfully!"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()
            print("MySQL connection is closed")