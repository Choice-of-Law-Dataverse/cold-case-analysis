"""Sub-agents for the CoLD Case Analyzer using OpenAI Agents SDK."""

import logging

from agents import Agent

from prompts.prompt_selector import get_prompt_module

from .models import (
    CaseAbstract,
    ChoiceOfLawExtraction,
    ChoiceOfLawIssue,
    CourtsPosition,
    DissentingOpinions,
    JurisdictionDetection,
    ObiterDicta,
    PILProvisions,
    RelevantFacts,
    ThemeClassification,
)

logger = logging.getLogger(__name__)


def create_jurisdiction_agent() -> Agent:
    """Create an agent for detecting jurisdiction."""
    return Agent(
        name="JurisdictionDetector",
        instructions="""You are an expert in legal systems and jurisdictions specializing in Private International Law.

Your task is to analyze a court decision and determine:
1. The legal system type (Civil-law, Common-law, or Indian jurisdiction)
2. The precise jurisdiction (e.g., Switzerland, USA, India, UK, etc.)
3. Your confidence level in this determination
4. Your reasoning for this determination

Look for indicators such as:
- Court names and structure
- Legal citations and references
- Language and terminology used
- References to specific legal codes or precedents
- The style of reasoning (precedent-based vs. code-based)

Be thorough and provide clear reasoning for your determination.""",
        output_type=JurisdictionDetection,
    )


def create_col_extraction_agent(jurisdiction: str = "Civil-law jurisdiction", precise_jurisdiction: str | None = None) -> Agent:
    """Create an agent for extracting Choice of Law sections using battle-tested prompts.

    Args:
        jurisdiction: Legal system type (e.g., 'Civil-law jurisdiction')
        precise_jurisdiction: Specific jurisdiction (e.g., 'India')
    """
    # Get the appropriate prompt module based on jurisdiction
    prompt_module = get_prompt_module(jurisdiction, "col_section", precise_jurisdiction)
    col_prompt = prompt_module.COL_SECTION_PROMPT

    # Extract the instructions part of the prompt (everything before the text placeholder)
    # The prompt template uses {text} and {col_section} placeholders which we'll handle in the orchestrator
    instructions = col_prompt.split("\\nHere is the text of the Court Decision:")[0].strip()

    return Agent(
        name="ChoiceOfLawExtractor",
        instructions=f"""{instructions}

When extracting sections, provide:
1. A list of extracted sections as separate text blocks
2. Your confidence level (high/medium/low) based on the clarity of choice of law discussions
3. Your reasoning for selecting these sections

Focus on extracting the exact court language that addresses choice of law issues.""",
        output_type=ChoiceOfLawExtraction,
    )


def create_theme_classification_agent(
    available_themes: list[str], jurisdiction: str = "Civil-law jurisdiction", precise_jurisdiction: str | None = None
) -> Agent:
    """Create an agent for classifying PIL themes using battle-tested prompts.

    Args:
        available_themes: List of available theme options
        jurisdiction: Legal system type (e.g., 'Civil-law jurisdiction')
        precise_jurisdiction: Specific jurisdiction (e.g., 'India')
    """
    # Get the appropriate prompt module based on jurisdiction
    prompt_module = get_prompt_module(jurisdiction, "theme", precise_jurisdiction)
    theme_prompt = prompt_module.PIL_THEME_PROMPT

    # Extract the instructions part (everything before the themes table placeholder)
    instructions = theme_prompt.split("Here is the table with all keywords")[0].strip()

    # Create a formatted list of themes for the instructions
    theme_list = "\n".join(f"- {theme}" for theme in available_themes)

    return Agent(
        name="ThemeClassifier",
        instructions=f"""{instructions}

Available themes:
{theme_list}

Provide:
1. A list of themes that apply to this case
2. Your confidence level (high/medium/low)
3. Your reasoning for selecting these themes

Be as precise as possible in matching the case to the most specific applicable themes.""",
        output_type=ThemeClassification,
    )


def create_relevant_facts_agent(jurisdiction: str = "Civil-law jurisdiction", precise_jurisdiction: str | None = None) -> Agent:
    """Create an agent for extracting relevant facts using battle-tested prompts.

    Args:
        jurisdiction: Legal system type (e.g., 'Civil-law jurisdiction')
        precise_jurisdiction: Specific jurisdiction (e.g., 'India')
    """
    # Get the appropriate prompt module based on jurisdiction
    prompt_module = get_prompt_module(jurisdiction, "analysis", precise_jurisdiction)
    facts_prompt = prompt_module.FACTS_PROMPT

    # Extract the instructions part (before the Court Decision Text)
    instructions = facts_prompt.split("\\nCourt Decision Text:")[0].strip()

    return Agent(
        name="RelevantFactsExtractor",
        instructions=f"""{instructions}

Provide a single paragraph narrative (maximum 300 words) containing all essential facts relevant to the choice of law analysis.""",
        output_type=RelevantFacts,
    )


def create_pil_provisions_agent(jurisdiction: str = "Civil-law jurisdiction", precise_jurisdiction: str | None = None) -> Agent:
    """Create an agent for extracting PIL provisions using battle-tested prompts.

    Args:
        jurisdiction: Legal system type (e.g., 'Civil-law jurisdiction')
        precise_jurisdiction: Specific jurisdiction (e.g., 'India')
    """
    # Get the appropriate prompt module based on jurisdiction
    prompt_module = get_prompt_module(jurisdiction, "analysis", precise_jurisdiction)
    pil_prompt = prompt_module.PIL_PROVISIONS_PROMPT

    # Extract the instructions part (before the Court Decision Text)
    instructions = pil_prompt.split("\\nCourt Decision Text:")[0].strip()

    return Agent(
        name="PILProvisionsExtractor",
        instructions=f"""{instructions}

Provide a list of Private International Law provisions cited in the case, formatted as strings with provision number and instrument name.""",
        output_type=PILProvisions,
    )


def create_col_issue_agent(jurisdiction: str = "Civil-law jurisdiction", precise_jurisdiction: str | None = None) -> Agent:
    """Create an agent for identifying the Choice of Law issue using battle-tested prompts.

    Args:
        jurisdiction: Legal system type (e.g., 'Civil-law jurisdiction')
        precise_jurisdiction: Specific jurisdiction (e.g., 'India')
    """
    # Get the appropriate prompt module based on jurisdiction
    prompt_module = get_prompt_module(jurisdiction, "analysis", precise_jurisdiction)
    issue_prompt = prompt_module.COL_ISSUE_PROMPT

    # Extract the instructions part (before the classification definitions)
    instructions = issue_prompt.split("The issue in this case is related")[0].strip()

    return Agent(
        name="ChoiceOfLawIssueIdentifier",
        instructions=f"""{instructions}

State the issue as a general question that captures the choice of law problem addressed by the court.""",
        output_type=ChoiceOfLawIssue,
    )


def create_courts_position_agent(
    jurisdiction: str = "Civil-law jurisdiction", precise_jurisdiction: str | None = None
) -> Agent:
    """Create an agent for analyzing the court's position using battle-tested prompts.

    Args:
        jurisdiction: Legal system type (e.g., 'Civil-law jurisdiction')
        precise_jurisdiction: Specific jurisdiction (e.g., 'India')
    """
    # Get the appropriate prompt module based on jurisdiction
    prompt_module = get_prompt_module(jurisdiction, "analysis", precise_jurisdiction)
    position_prompt = prompt_module.COURTS_POSITION_PROMPT

    # Extract the instructions part (before the CONSTRAINTS)
    instructions = position_prompt.split("CONSTRAINTS:")[0].strip()

    return Agent(
        name="CourtsPositionAnalyzer",
        instructions=f"""{instructions}

CONSTRAINTS:
- Base the response on the provided judgment text and extracted sections only.
- Maintain a neutral and objective tone.
- Use a maximum of 300 words.

Provide a summary that generalizes the court's position so it can be applied to other PIL cases.""",
        output_type=CourtsPosition,
    )


def create_obiter_dicta_agent() -> Agent:
    """Create an agent for extracting obiter dicta (Common Law jurisdictions)."""
    return Agent(
        name="ObiterDictaExtractor",
        instructions="""You are a legal analyst specializing in Common Law case analysis.

Your task is to identify and extract obiter dicta - statements made by the court that are not essential to the decision.

Obiter dicta includes:
- Hypothetical scenarios discussed
- Alternative reasoning paths mentioned
- General commentary on the law
- Dicta on issues not directly before the court

Distinguish clearly between obiter dicta and ratio decidendi.
This is important for understanding the persuasive (but not binding) aspects of the decision.""",
        output_type=ObiterDicta,
    )


def create_dissenting_opinions_agent() -> Agent:
    """Create an agent for extracting dissenting opinions (Common Law jurisdictions)."""
    return Agent(
        name="DissentingOpinionsExtractor",
        instructions="""You are a legal analyst specializing in judicial opinions.

Your task is to identify and summarize any dissenting opinions in the case.

Include:
- Which judge(s) dissented
- The basis for the dissent
- Alternative reasoning or interpretation proposed
- Key points of disagreement with the majority

Dissenting opinions can provide valuable insight into alternative approaches to Choice of Law issues.""",
        output_type=DissentingOpinions,
    )


def create_abstract_agent(jurisdiction: str = "Civil-law jurisdiction", precise_jurisdiction: str | None = None) -> Agent:
    """Create an agent for generating the case abstract using battle-tested prompts.

    Args:
        jurisdiction: Legal system type (e.g., 'Civil-law jurisdiction')
        precise_jurisdiction: Specific jurisdiction (e.g., 'India')
    """
    # Get the appropriate prompt module based on jurisdiction
    prompt_module = get_prompt_module(jurisdiction, "analysis", precise_jurisdiction)
    abstract_prompt = prompt_module.ABSTRACT_PROMPT

    # Extract the instructions part (before Court Decision Text)
    instructions = abstract_prompt.split("\\nCourt Decision Text:")[0].strip()

    return Agent(
        name="AbstractGenerator",
        instructions=f"""{instructions}

Create a single paragraph (maximum 300 words, maximum 4 sentences) that synthesizes the facts, PIL issues, court's reasoning, and precedential outcome.""",
        output_type=CaseAbstract,
    )
