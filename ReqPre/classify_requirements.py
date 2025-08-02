import pandas as pd
import csv
import os
import google.generativeai as genai
# from openai import OpenAI # Uncomment and install if using OpenAI GPT

# --- LLM Integration Placeholder ---
# You will need to replace this with your actual LLM integration.
# Example for Google Gemini:
# model = GenerativeModel(model_name="gemini-pro", api_key=os.getenv("GOOGLE_API_KEY"))
#
# Example for OpenAI GPT:
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_requirement(requirement_text: str) -> dict:
    """
    Classifies a single software requirement into role, action, goal, and acceptance_criteria
    using an LLM.
    """
    # --- Replace this section with your LLM call ---
    # This is a placeholder for demonstration purposes.
    # In a real scenario, you would send the prompt to your LLM and parse its response.

    prompt = f'''You are an expert at classifying software requirements from GitHub issue-style reports.

Given a cleaned requirement text, extract 4 fields:
- `role`: Who is acting or facing the issue? (e.g., User, Developer, System)
- `action`: The key action/complaint being described.
- `goal`: What outcome is desired or expected?
- `acceptance_criteria`: What would confirm this is resolved?

Example:
Input: "When ctrl-clicking a file link with a `.\` prefix, the file is not found. Removing the prefix manually works. This is frustrating."
Output:
{{
  "role": "User",
  "action": "ctrl-click file link fails due to .\\ prefix",
  "goal": "open file directly from terminal",
  "acceptance_criteria": "File opens directly with ctrl-click regardless of .\\ prefix"
}}

Now classify the following requirement and return a JSON object with the four fields:
Input: "{requirement_text}"
Output:'''

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_name="gemini-pro")
    response = model.generate_content(prompt)
    classified_data_str = response.text
    
    try:
        # Assuming the LLM returns a JSON string
        import json
        return json.loads(classified_data_str)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from LLM response: {classified_data_str}")
        return {
            "role": "Error",
            "action": "LLM response not valid JSON",
            "goal": "N/A",
            "acceptance_criteria": "N/A"
        }


def main():
    input_csv_path = "cleaned_requirements.csv"
    output_csv_path = "classified_requirements.csv"

    script_dir = os.path.dirname(__file__)
    full_input_path = os.path.join(script_dir, input_csv_path)
    full_output_path = os.path.join(script_dir, output_csv_path)

    classified_data = []

    try:
        with open(full_input_path, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader)  # Skip header row
            
            # Add new headers for the output CSV
            output_header = ['req_id', 'raw_text', 'role', 'action', 'goal', 'acceptance_criteria']
            classified_data.append(output_header)

            for i, row in enumerate(reader):
                req_id = row[0]
                raw_text = row[1]

                print(f"Classifying requirement {req_id}...")
                try:
                    classified_fields = classify_requirement(raw_text)
                    classified_data.append([
                        req_id,
                        raw_text,
                        classified_fields.get("role", ""),
                        classified_fields.get("action", ""),
                        classified_fields.get("goal", ""),
                        classified_fields.get("acceptance_criteria", "")
                    ])
                except Exception as e:
                    print(f"Error classifying requirement {req_id}: {e}")
                    classified_data.append([
                        req_id,
                        raw_text,
                        "Error", "Error", "Error", "Error"
                    ])

        with open(full_output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(classified_data)

        print(f"\nClassification complete. Output saved to {full_output_path}")

    except FileNotFoundError:
        print(f"Error: {input_csv_path} not found in {script_dir}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
