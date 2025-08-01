from src.agent import generate_test_cases
from src.utils.file_utils import read_file
from dotenv import load_dotenv
import re

def main():
    load_dotenv()
    """Main function."""
    
    file_path = "Coding/development_requirements.md"
    full_content = read_file(file_path)

    # Split the content into individual user stories
    user_story_blocks = re.split(r'### Rank \d+:', full_content)
    
    print("--- Generated Test Cases ---\n")

    for block in user_story_blocks:
        if block.strip():
            user_story_match = re.search(r'\*\*User Story:\*\*\s*(.*?)\n', block, re.DOTALL)
            dev_considerations_match = re.search(r'\*\*Development Considerations:\*\*\s*(.*?)(?=\n### Rank \d+:|\Z)', block, re.DOTALL)

            if user_story_match and dev_considerations_match:
                user_story = user_story_match.group(1).strip()
                development_considerations = dev_considerations_match.group(1).strip()

                print(f"Generating Test Cases for: {user_story.splitlines()[0]}...")
                test_cases_obj = generate_test_cases(user_story, development_considerations)

                for tc in test_cases_obj.test_cases:
                    print(f"  Test Case ID: {tc.id}")
                    print(f"  Description: {tc.description}")
                    preconditions_str = "\n    ".join(tc.preconditions)
                    print(f"  Preconditions: {preconditions_str}")
                    steps_str = "\n    ".join(tc.steps)
                    print(f"  Steps: {steps_str}")
                    print(f"  Expected Result: {tc.expected_result}")
                    print(f"  Test Type: {tc.test_type}")
                    print("  " + "-" * 20)
                print("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    main()
