# Project Documentation: User Story Analysis Agent

This project utilizes a Large Language Model (LLM) to analyze user stories, providing structured feedback on specification refinement and prioritization.

## Project Flow

1.  **Initialization (`main.py`):**
    *   Loads environment variables (e.g., `GOOGLE_API_KEY`) from `.env`.
    *   Reads the user story content from a specified file (e.g., `user_story.txt` or PDF).

2.  **Specification Refinement (`get_specification_refinement`):**
    *   The user story is passed to this function.
    *   An LLM (Gemini) is prompted to act as a QA Engineer.
    *   It identifies ambiguities, contradictions, missing edge cases, and non-functional requirements.
    *   Output is structured according to the `SpecificationRefinement` Pydantic model.

3.  **Prioritization (`get_prioritization`):**
    *   The user story is passed to this function.
    *   An LLM (Gemini) is prompted to act as a Product Owner.
    *   It estimates the RICE score (Reach, Impact, Confidence, Effort) and provides justification.
    *   Output is structured according to the `Prioritization` Pydantic model.

4.  **Output:**
    *   Both the specification refinement and prioritization results are printed to the console.

## Role of LangChain

LangChain is a framework that streamlines LLM application development. In this project, it is used for:

*   **Prompt Engineering:** Crafting clear, role-based prompts for the LLM.
*   **LLM Integration:** Providing a standardized interface to interact with Google's Gemini models.
*   **Structured Output:** Enforcing that the LLM's responses adhere to predefined Pydantic schemas (`SpecificationRefinement`, `Prioritization`), making the output easily consumable by the application.
*   **Chains:** Combining prompts, LLMs, and structured output parsing into coherent, executable sequences.

LangChain abstracts away much of the complexity of direct LLM interaction, enabling efficient development of intelligent agents.