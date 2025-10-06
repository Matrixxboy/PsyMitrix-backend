from Models import Question

import json

def save_question_to_db(content, question_data, connection, cursor):
    try:
        sql = "INSERT INTO questions (question, question_type) VALUES (%s, %s)"
        val = (question_data['question'], question_data['question_type'])
        cursor.execute(sql, val)
        connection.commit()
        print(f" {content} inserted successfully.")
        print(f"Question saved to DB with ID: {cursor.lastrowid}")
    except Exception as e:
        print(f"Error saving question to DB: {str(e)}")