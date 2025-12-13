"""
Unit tests for Claude Code Subagents
Tests spec validation, agent execution, and API endpoints
"""

import pytest
import yaml
from pathlib import Path
import sys
import os

# Add server to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.agent_base import AgentBase
from agents.summarizer_agent import SummarizerAgent
from agents.quiz_generator_agent import QuizGeneratorAgent
from agents.code_explainer_agent import CodeExplainerAgent

class TestAgentSpecs:
    """Test agent YAML specifications"""

    def test_summarizer_spec_exists(self):
        """Test that summarizer spec file exists and is valid YAML"""
        spec_path = Path(__file__).parent.parent.parent / "spec" / "agents" / "summarizer.yaml"
        assert spec_path.exists(), "summarizer.yaml not found"

        with open(spec_path) as f:
            spec = yaml.safe_load(f)

        assert spec['name'] == 'summarizer'
        assert 'inputs' in spec
        assert 'outputs' in spec
        assert 'prompt_template' in spec

    def test_quiz_generator_spec_exists(self):
        """Test that quiz-generator spec file exists and is valid YAML"""
        spec_path = Path(__file__).parent.parent.parent / "spec" / "agents" / "quiz-generator.yaml"
        assert spec_path.exists(), "quiz-generator.yaml not found"

        with open(spec_path) as f:
            spec = yaml.safe_load(f)

        assert spec['name'] == 'quiz-generator'
        assert 'inputs' in spec
        assert 'outputs' in spec

    def test_code_explainer_spec_exists(self):
        """Test that code-explainer spec file exists and is valid YAML"""
        spec_path = Path(__file__).parent.parent.parent / "spec" / "agents" / "code-explainer.yaml"
        assert spec_path.exists(), "code-explainer.yaml not found"

        with open(spec_path) as f:
            spec = yaml.safe_load(f)

        assert spec['name'] == 'code-explainer'
        assert 'inputs' in spec
        assert 'outputs' in spec

    def test_spec_schema_validation(self):
        """Test that all specs follow required schema"""
        required_fields = ['name', 'version', 'description', 'inputs', 'outputs', 'prompt_template']

        for agent_name in ['summarizer', 'quiz-generator', 'code-explainer']:
            spec_path = Path(__file__).parent.parent.parent / "spec" / "agents" / f"{agent_name}.yaml"

            with open(spec_path) as f:
                spec = yaml.safe_load(f)

            for field in required_fields:
                assert field in spec, f"{agent_name} missing required field: {field}"

            # Validate inputs structure
            for input_name, input_spec in spec['inputs'].items():
                assert 'type' in input_spec, f"{agent_name}.{input_name} missing type"
                assert 'description' in input_spec, f"{agent_name}.{input_name} missing description"


class TestAgentValidation:
    """Test agent input validation"""

    def test_summarizer_required_fields(self):
        """Test summarizer validates required fields"""
        # Mock API key to avoid needing real one
        os.environ['OPENAI_API_KEY'] = 'test-key'

        agent = SummarizerAgent()

        # Missing required 'text' field
        with pytest.raises(ValueError, match="Required field missing: text"):
            agent.validate_input({})

    def test_summarizer_enum_validation(self):
        """Test summarizer validates enum values"""
        os.environ['OPENAI_API_KEY'] = 'test-key'
        agent = SummarizerAgent()

        # Invalid summary_type
        with pytest.raises(ValueError, match="must be one of"):
            agent.validate_input({
                "text": "Test text",
                "summary_type": "invalid_type"
            })

    def test_quiz_generator_range_validation(self):
        """Test quiz generator validates integer ranges"""
        os.environ['OPENAI_API_KEY'] = 'test-key'
        agent = QuizGeneratorAgent()

        # Question count below minimum
        with pytest.raises(ValueError, match="below minimum"):
            agent.validate_input({
                "content": "Test content",
                "question_count": 0
            })

        # Question count above maximum
        with pytest.raises(ValueError, match="above maximum"):
            agent.validate_input({
                "content": "Test content",
                "question_count": 25
            })

    def test_code_explainer_default_values(self):
        """Test code explainer applies default values"""
        os.environ['OPENAI_API_KEY'] = 'test-key'
        agent = CodeExplainerAgent()

        validated = agent.validate_input({
            "code": "print('hello')"
        })

        assert validated['language'] == 'python'  # default
        assert validated['explanation_level'] == 'intermediate'  # default


class TestAgentPromptRendering:
    """Test prompt template rendering"""

    def test_summarizer_prompt_rendering(self):
        """Test summarizer renders prompt correctly"""
        os.environ['OPENAI_API_KEY'] = 'test-key'
        agent = SummarizerAgent()

        inputs = {
            "text": "Test chapter content about ROS",
            "summary_type": "balanced"
        }

        prompt = agent.render_prompt(inputs)

        assert "Test chapter content about ROS" in prompt
        assert "balanced" in prompt
        assert "{{text}}" not in prompt  # Template variables should be replaced

    def test_quiz_generator_prompt_rendering(self):
        """Test quiz generator renders prompt with array"""
        os.environ['OPENAI_API_KEY'] = 'test-key'
        agent = QuizGeneratorAgent()

        inputs = {
            "content": "Test content",
            "question_count": 5,
            "difficulty": "intermediate",
            "question_types": ["multiple_choice", "true_false"]
        }

        prompt = agent.render_prompt(inputs)

        assert "5" in prompt
        assert "intermediate" in prompt
        assert "multiple_choice" in prompt or "true_false" in prompt


class TestAgentParsing:
    """Test response parsing"""

    def test_summarizer_parsing(self):
        """Test summarizer parses AI response correctly"""
        os.environ['OPENAI_API_KEY'] = 'test-key'
        agent = SummarizerAgent()

        ai_response = """
        This is a comprehensive summary of the chapter covering ROS fundamentals.
        The chapter introduces key concepts for robotics programming.

        Key Takeaways:
        - ROS provides a framework for robot development
        - Topics and nodes enable modular architecture
        - URDF is used for robot modeling
        """

        inputs = {"text": "Original text here " * 100}
        result = agent.parse_response(ai_response, inputs)

        assert 'summary' in result
        assert 'key_points' in result
        assert 'word_count' in result
        assert len(result['key_points']) > 0
        assert result['word_count'] > 0

    def test_code_explainer_section_parsing(self):
        """Test code explainer parses sections correctly"""
        os.environ['OPENAI_API_KEY'] = 'test-key'
        agent = CodeExplainerAgent()

        ai_response = """
        ## Overview
        This code creates a ROS publisher for velocity commands.

        ## Line-by-Line Explanation
        Line 1: import rospy - Imports ROS Python library
        Line 2: from geometry_msgs.msg import Twist - Imports Twist message type

        ## Key Concepts
        - **ROS Publisher**: Publishers send messages to topics
        - **Twist Message**: Represents velocity in 3D space

        ## Common Pitfalls
        - Forgetting to call rospy.init_node()
        - Not checking rospy.is_shutdown()
        """

        result = agent.parse_response(ai_response, {})

        assert 'overview' in result
        assert 'line_by_line' in result
        assert 'key_concepts' in result
        assert 'common_pitfalls' in result
        assert len(result['common_pitfalls']) > 0


# Integration test (requires API key - mark as skipif no key)
@pytest.mark.skipif(
    not os.getenv('OPENAI_API_KEY') and not os.getenv('CLAUDE_API_KEY'),
    reason="No API key configured"
)
class TestAgentIntegration:
    """Integration tests with actual AI APIs (requires API key)"""

    @pytest.mark.asyncio
    async def test_summarizer_execution(self):
        """Test full summarizer execution with real API"""
        agent = SummarizerAgent()

        result = await agent.execute({
            "text": "Forward kinematics is the process of calculating the position and orientation of a robot's end-effector given the joint angles. It uses transformation matrices to represent rotations and translations.",
            "summary_type": "concise"
        })

        assert 'summary' in result
        assert 'key_points' in result
        assert 'metadata' in result
        assert result['metadata']['agent'] == 'summarizer'
        assert result['word_count'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
