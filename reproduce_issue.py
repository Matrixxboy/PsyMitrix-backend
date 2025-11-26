
import os
import sys
from unittest.mock import MagicMock

# Add the project root to sys.path
sys.path.append(os.path.abspath("e:/Utsav/Personal Projects/PsyMitrix-backend"))

# Mock OpenAI and toon to avoid actual API calls and dependencies
sys.modules["openai"] = MagicMock()
sys.modules["toon"] = MagicMock()

from AI.aiModel import generate_questions
from Models.Models import IntakeParameters, questions, Question

def test_generate_questions_error():
    params = IntakeParameters(Name="Test User")
    
    # Create a list of questions as expected by the endpoint
    q1 = Question(question="Q1", question_type="text", answer="A1")
    q_list = questions(questions=[q1])
    
    print("Attempting to call generate_questions...")
    try:
        generate_questions(params, q_list)
        print("SUCCESS: generate_questions completed without error.")
    except AttributeError as e:
        print(f"CAUGHT EXPECTED ERROR: {e}")
    except Exception as e:
        print(f"CAUGHT UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_generate_questions_error()
