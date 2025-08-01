import os
from langchain_core.prompts import ChatPromptTemplate
from pydantic.v1 import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from MCP.mcp_core import Message, Context

class SpecificationRefinement(BaseModel):
    """Model for the Specification Refinement agent."""
    ambiguities: list[str] = Field(description="A list of ambiguities found in the user story.")
    contradictions: list[str] = Field(description="A list of contradictions found in the user story.")
    missing_edge_cases: list[str] = Field(description="A list of missing edge cases in the user story.")
    non_functional_requirements: list[str] = Field(description="A list of non-functional requirements that are missing from the user story.")
    questions: list[str] = Field(description="A list of questions to ask the product owner to resolve the issues.")

class Prioritization(BaseModel):
    """Model for the Prioritization agent."""
    reach: int = Field(description="The reach of the user story (1-10).")
    impact: int = Field(description="The impact of the user story (1-10).")
    confidence: int = Field(description="The confidence in the user story (0-100).")
    effort: int = Field(description="The effort required to implement the user story (in person-weeks).")
    justification: str = Field(description="A brief justification for the scores.")

class TestCase(BaseModel):
    """Model for a single test case."""
    id: str = Field(description="Unique identifier for the test case (e.g., TC-001).")
    description: str = Field(description="A clear description of what the test case is verifying.")
    preconditions: list[str] = Field(description="Any conditions that must be met before executing the test.")
    steps: list[str] = Field(description="A list of actions to perform to execute the test.")
    expected_result: str = Field(description="The expected outcome if the test passes.")
    test_type: str = Field(description="Type of test (e.g., Positive, Negative, Edge Case, Performance, Security).")

class TestCases(BaseModel):
    """Model for a list of test cases for a given feature/user story."""
    test_cases: list[TestCase] = Field(description="A list of test cases.")

def get_specification_refinement(user_story: str) -> SpecificationRefinement:
    """Returns a specification refinement for a user story."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a meticulous QA Engineer. Review the following user story and its acceptance criteria. Identify any potential ambiguities, logical contradictions, missing edge cases, or non-functional requirements (e.g., performance, security). Suggest specific questions to ask the product owner to resolve these issues."),
        ("user", "{user_story}")
    ])
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", google_api_key=os.getenv("GOOGLE_API_KEY"))
    structured_llm = llm.with_structured_output(SpecificationRefinement)
    chain = prompt | structured_llm
    return chain.invoke({"user_story": user_story})

def get_prioritization(user_story: str) -> Prioritization:
    """Returns a prioritization for a user story."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an experienced Product Owner. For the following user story, estimate the RICE score. Provide a score from 1-10 for Reach and Impact, a percentage for Confidence (0-100%), and an estimate in person-weeks for Effort. Provide a brief justification for each score. Output as a JSON object."),
        ("user", "{user_story}")
    ])
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", google_api_key=os.getenv("GOOGLE_API_KEY"))
    structured_llm = llm.with_structured_output(Prioritization)
    chain = prompt | structured_llm
    return chain.invoke({"user_story": user_story})

def generate_test_cases(input_message: Message, context: Context) -> Message:
    """Generates test cases for a given user story and its development considerations, using MCP Message and Context."""
    user_story = input_message.content.get("user_story", "")
    development_considerations = input_message.content.get("development_considerations", "")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a meticulous QA Engineer. Generate comprehensive test cases (positive, negative, edge cases, performance, security) for the given user story and its development considerations. Provide clear IDs, descriptions, preconditions, steps, expected results, and test types."),
        ("user", f"User Story: {user_story}\nDevelopment Considerations: {development_considerations}")
    ])
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", google_api_key=os.getenv("GOOGLE_API_KEY"))
    structured_llm = llm.with_structured_output(TestCases)
    chain = prompt | structured_llm
    test_cases_obj = chain.invoke({"user_story": user_story, "development_considerations": development_considerations})

    # Update context if needed (e.g., store generated test cases)
    if context.shared_analysis_results is None:
        context.shared_analysis_results = {}
    context.shared_analysis_results["generated_test_cases"] = test_cases_obj.dict() # Store as dictionary

    return Message(
        sender="CodingAgent",
        receiver="Orchestrator", # Or the next intended agent
        content={"test_cases": test_cases_obj.dict()}, # Convert Pydantic model to dict for Message content
        message_type="test_cases_generated"
    )