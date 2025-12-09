import json
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.pdf_service import generate_personality_pdf

def test_pdf_generation():
    print("Testing PDF Generation...")
    
    # Load the data that caused the error
    json_path = "new_response_data.json"
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    try:
        with open(json_path, "r") as f:
            # The file contains a stringified JSON in the first key or something? 
            # Let's check the format based on previous view_file
            # The previous view_file showed the file content is a JSON string *inside* a string?
            # No, looking at step 76, it looks like a string that contains escaped JSON.
            # "{\n  \"sections\": ... }" -> This is a JSON string.
            content = f.read()
            
            # If it's double serialized (string inside json), parse it
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # Maybe it's just raw json?
                data = content
                
            # If data is a string, parse it again because the report.py logic does:
            # report_cleaned = json.loads(report_data)
            if isinstance(data, str):
                data = json.loads(data)
                
    except Exception as e:
        print(f"Error processing JSON: {e}")
        return

    output_filename = "test_report.pdf"
    
    try:
        generate_personality_pdf(output_filename, data, "Test User", "Tester")
        print(f"Success! PDF generated at {output_filename}")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()
