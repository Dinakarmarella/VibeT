import csv
import re
import os

def clean_text(text):
    # Remove non-alphanumeric characters, but keep spaces
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

def contains_only_alphanumeric_details(text):
    # This is a heuristic to detect if the line is just a list of alphanumeric details.
    # We assume that if a line has a very long string of characters without a space,
    # it is likely a system detail or some other non-requirement text.
    words = text.split()
    if any(len(word) > 40 for word in words):
        return True
    return False

def main():
    input_csv_path = "raw_requirements.csv"
    output_csv_path = "cleaned_requirements.csv"

    script_dir = os.path.dirname(__file__)
    full_input_path = os.path.join(script_dir, input_csv_path)
    full_output_path = os.path.join(script_dir, output_csv_path)

    cleaned_data = []

    try:
        with open(full_input_path, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader)  # Skip header row
            cleaned_data.append(header)

            for row in reader:
                if len(row) < 2:
                    continue

                req_id = row[0]
                raw_text = row[1]

                # 1) If column A is not a number delete that row
                if not req_id.isdigit():
                    continue

                # 2) remove the whole line with <img> tags
                if '<img' in raw_text.lower():
                    continue

                # 3) remove special characters which is not alpha numerical
                cleaned = clean_text(raw_text)

                # 4) Can see some alphanumeric details also fetching i it ,you can dlet such rows
                if contains_only_alphanumeric_details(cleaned):
                    continue

                # Add the cleaned row to the list
                cleaned_data.append([req_id, cleaned.strip()])

        with open(full_output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(cleaned_data)

        print(f"\nCleaning complete. Output saved to {full_output_path}")

    except FileNotFoundError:
        print(f"Error: {input_csv_path} not found in {script_dir}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
