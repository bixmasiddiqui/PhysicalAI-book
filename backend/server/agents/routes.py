"""
API Routes for Claude Code Subagents
Exposes summarizer, quiz-generator, and code-explainer endpoints
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import traceback

from .summarizer_agent import SummarizerAgent
from .quiz_generator_agent import QuizGeneratorAgent
from .code_explainer_agent import CodeExplainerAgent

router = APIRouter()

# Request models
class SummarizerRequest(BaseModel):
    text: str = Field(..., description="Text to summarize")
    summary_type: Optional[str] = Field("balanced", description="concise | balanced | detailed")
    focus_area: Optional[str] = Field(None, description="Specific area to focus on")

class QuizGeneratorRequest(BaseModel):
    content: str = Field(..., description="Content to generate quiz from")
    question_count: Optional[int] = Field(5, ge=1, le=20, description="Number of questions")
    difficulty: Optional[str] = Field("mixed", description="beginner | intermediate | advanced | mixed")
    question_types: Optional[List[str]] = Field(
        ["multiple_choice", "true_false"],
        description="Types of questions to include"
    )

class CodeExplainerRequest(BaseModel):
    code: str = Field(..., description="Code snippet to explain")
    language: Optional[str] = Field("python", description="Programming language")
    explanation_level: Optional[str] = Field("intermediate", description="beginner | intermediate | advanced")
    context: Optional[str] = Field(None, description="Additional context")

# Response models
class AgentResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None

@router.post("/summarizer", response_model=AgentResponse, tags=["Agents"])
async def summarize_text(request: SummarizerRequest):
    """
    Summarize textbook content

    **Example Request:**
    ```json
    {
        "text": "Forward kinematics calculates the position...",
        "summary_type": "balanced"
    }
    ```

    **Returns:** Summary, key points, word count, compression ratio
    """
    try:
        agent = SummarizerAgent()

        result = await agent.execute({
            "text": request.text,
            "summary_type": request.summary_type,
            "focus_area": request.focus_area
        })

        return AgentResponse(success=True, data=result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Summarizer error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )

@router.post("/quiz-generator", response_model=AgentResponse, tags=["Agents"])
async def generate_quiz(request: QuizGeneratorRequest):
    """
    Generate educational quiz from content

    **Example Request:**
    ```json
    {
        "content": "ROS (Robot Operating System) is a framework...",
        "question_count": 3,
        "difficulty": "intermediate",
        "question_types": ["multiple_choice", "true_false"]
    }
    ```

    **Returns:** Array of quiz questions with answers and explanations
    """
    try:
        agent = QuizGeneratorAgent()

        result = await agent.execute({
            "content": request.content,
            "question_count": request.question_count,
            "difficulty": request.difficulty,
            "question_types": request.question_types
        })

        return AgentResponse(success=True, data=result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Quiz generator error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )

@router.post("/code-explainer", response_model=AgentResponse, tags=["Agents"])
async def explain_code(request: CodeExplainerRequest):
    """
    Explain code snippet with line-by-line analysis

    **Example Request:**
    ```json
    {
        "code": "import rospy\\nfrom geometry_msgs.msg import Twist\\n...",
        "language": "python",
        "explanation_level": "intermediate",
        "context": "Chapter 3: ROS Programming"
    }
    ```

    **Returns:** Overview, line-by-line breakdown, key concepts, pitfalls, suggestions
    """
    try:
        agent = CodeExplainerAgent()

        result = await agent.execute({
            "code": request.code,
            "language": request.language,
            "explanation_level": request.explanation_level,
            "context": request.context
        })

        return AgentResponse(success=True, data=result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Code explainer error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )

@router.get("/agents/list", tags=["Agents"])
async def list_agents():
    """List all available agents with their capabilities"""
    return {
        "agents": [
            {
                "name": "summarizer",
                "endpoint": "/api/agent/summarizer",
                "description": "Summarize textbook chapters or sections",
                "inputs": ["text", "summary_type", "focus_area"],
                "outputs": ["summary", "key_points", "word_count", "metadata"]
            },
            {
                "name": "quiz-generator",
                "endpoint": "/api/agent/quiz-generator",
                "description": "Generate educational quizzes from content",
                "inputs": ["content", "question_count", "difficulty", "question_types"],
                "outputs": ["questions", "metadata"]
            },
            {
                "name": "code-explainer",
                "endpoint": "/api/agent/code-explainer",
                "description": "Explain code with line-by-line analysis",
                "inputs": ["code", "language", "explanation_level", "context"],
                "outputs": ["overview", "line_by_line", "key_concepts", "common_pitfalls", "suggested_modifications"]
            }
        ]
    }

@router.get("/agents/{agent_name}/spec", tags=["Agents"])
async def get_agent_spec(agent_name: str):
    """Get the YAML specification for a specific agent"""
    try:
        if agent_name == "summarizer":
            agent = SummarizerAgent()
        elif agent_name == "quiz-generator":
            agent = QuizGeneratorAgent()
        elif agent_name == "code-explainer":
            agent = CodeExplainerAgent()
        else:
            raise HTTPException(status_code=404, detail="Agent not found")

        return agent.spec

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Agent specification not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
