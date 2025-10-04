"""Sub-agents for the CoLD Case Analyzer using OpenAI Agents SDK."""

import logging

from agents import Agent

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


def create_col_extraction_agent() -> Agent:
    """Create an agent for extracting Choice of Law sections."""
    return Agent(
        name="ChoiceOfLawExtractor",
        instructions="""You are an expert in Private International Law and Choice of Law analysis.

Your task is to identify and extract all sections of the court decision that deal with Choice of Law issues.

Choice of Law sections typically include:
- Discussion of which jurisdiction's law applies
- Conflict of laws analysis
- Forum selection considerations
- Recognition and enforcement of foreign judgments
- Applicable law determination
- Connecting factors analysis

Extract complete sections or paragraphs, not just snippets. Include enough context to understand the court's reasoning.
Provide your confidence level and explain why you selected these particular sections.""",
        output_type=ChoiceOfLawExtraction,
    )


def create_theme_classification_agent(available_themes: list[str]) -> Agent:
    """Create an agent for classifying PIL themes."""
    theme_list = "\n".join(f"- {theme}" for theme in available_themes)
    return Agent(
        name="ThemeClassifier",
        instructions=f"""You are an expert in Private International Law (PIL) theme classification.

Your task is to analyze the case and classify it according to the relevant PIL themes.

Available themes:
{theme_list}

Analyze the case and select all themes that are relevant. A case may have multiple themes.
Provide your confidence level and explain how you arrived at these theme classifications.

Focus on the substantive PIL issues, not procedural matters unless they are central to the case.""",
        output_type=ThemeClassification,
    )


def create_relevant_facts_agent() -> Agent:
    """Create an agent for extracting relevant facts."""
    return Agent(
        name="RelevantFactsExtractor",
        instructions="""You are a legal analyst specializing in case analysis.

Your task is to extract and summarize the relevant factual background of the case that is pertinent to the Choice of Law analysis.

Include:
- Key parties and their relationships
- Relevant locations and cross-border elements
- Timeline of important events
- Facts that influenced the Choice of Law determination

Be concise but comprehensive. Focus on facts that matter for the PIL analysis.""",
        output_type=RelevantFacts,
    )


def create_pil_provisions_agent() -> Agent:
    """Create an agent for extracting PIL provisions."""
    return Agent(
        name="PILProvisionsExtractor",
        instructions="""You are an expert in Private International Law.

Your task is to identify and extract all Private International Law provisions, statutes, conventions, and legal instruments cited or applied in the case.

Include:
- International conventions (e.g., Hague Conventions, Rome I/II)
- National PIL statutes and codes
- Bilateral treaties
- Customary international law principles
- Relevant case law precedents on PIL issues

Provide the full citation for each provision when available.""",
        output_type=PILProvisions,
    )


def create_col_issue_agent() -> Agent:
    """Create an agent for identifying the Choice of Law issue."""
    return Agent(
        name="ChoiceOfLawIssueIdentifier",
        instructions="""You are an expert in Choice of Law analysis.

Your task is to clearly identify and articulate the Choice of Law issue(s) that the court addressed in this case.

The issue should be stated as a question or problem that the court needed to resolve, such as:
- Which law applies to X?
- How should connecting factors be interpreted?
- Whether a particular exception applies?

Be precise and comprehensive. If there are multiple issues, address all of them.""",
        output_type=ChoiceOfLawIssue,
    )


def create_courts_position_agent() -> Agent:
    """Create an agent for analyzing the court's position."""
    return Agent(
        name="CourtsPositionAnalyzer",
        instructions="""You are a legal analyst specializing in judicial reasoning.

Your task is to analyze and summarize the court's reasoning and position on the Choice of Law issue.

Include:
- The court's legal reasoning and methodology
- How the court applied relevant provisions
- The court's interpretation of connecting factors
- The outcome and its rationale
- Any important distinctions or qualifications made

This should capture the ratio decidendi (binding reasoning) of the case.
Be comprehensive but well-organized.""",
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


def create_abstract_agent() -> Agent:
    """Create an agent for generating the case abstract."""
    return Agent(
        name="AbstractGenerator",
        instructions="""You are a legal analyst specializing in case summaries.

Your task is to create a concise abstract of the case focusing on its Choice of Law aspects.

The abstract should include:
- Brief case background
- The Choice of Law issue(s)
- The court's holding
- The significance of the decision

This should be 3-5 sentences that give a reader a quick understanding of the case and its PIL importance.
Be clear and accessible while maintaining legal precision.""",
        output_type=CaseAbstract,
    )
