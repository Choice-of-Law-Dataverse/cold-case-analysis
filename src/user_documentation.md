# CoLD Case Analyzer - User Guide for Legal Specialists

The CoLD Case Analyzer is an AI-powered tool that systematically analyzes court decisions for private international law issues. This guide provides step-by-step instructions for legal professionals to effectively use the system.

## Getting Started

Optional login provides access to advanced AI models (o3, o4-mini), while guest users can access the basic model (gpt-4.1-nano). Select your preferred model from the dropdown. Enter the case citation for record-keeping, then enter the complete court decision text. You can either upload a PDF and revise the automatically extracted text or paste the text of the court decision into the input field. Use "Use Demo Case" to load a sample Swiss case for practice.

The system processes cases through eight sequential phases: jurisdiction detection, choice of law section extraction, theme classification, and five-step legal analysis. Each phase includes AI generation followed by expert evaluation and optional refinement.

**Jurisdiction Detection and Validation**: Click "Detect Jurisdiction" to automatically classify the decision as Civil-law, Common-law, or no court decision. The system uses jurisdiction-specific prompts optimized for different legal systems. Review the classification and provide an accuracy score (0-100). Use the dropdown to confirm or modify the detection before proceeding. This step is critical as it determines which specialized prompts will be used throughout the analysis.

**Choice of Law Section Extraction**: Click "Extract COL Section" to identify sections containing choice of law information. The system focuses on PIL-relevant content while filtering out procedural details. Score the extraction quality, then either provide specific feedback for iterative improvement or proceed directly to editing. Multiple feedback rounds can refine extraction accuracy. When satisfied, edit the extracted section directly and submit to advance to theme classification.

**Theme Classification**: The system automatically assigns PIL themes from a predefined taxonomy including concepts like party autonomy, observance of choice of law clauses, arbitration, principles (soft law), non-state law, comparative method, and connecting factors. Score the classification quality, then use the multi-select interface to adjust theme assignments. Select only clearly applicable themes to maintain classification accuracy. Themes inform subsequent analysis steps and should reflect the core PIL issues in the case.

## Legal Analysis Process

The system conducts systematic analysis across five dimensions, each building on previous steps:

**Abstract**: For civil-law cases, the system extracts the official abstract and translates it to English. For other cases or when no official abstract exists, it generates a concise summary covering the dispute topic, key provisions, and legal issues. Edit to ensure accuracy and conciseness.

**Relevant Facts**: Extraction focuses on factual background essential for understanding the choice of law dispute, including party identification, international elements, contractual relationships, and procedural history. The system prioritizes facts relevant to PIL analysis while avoiding extraneous details. Ensure factual accuracy and completeness.

**Private International Law Provisions**: The system identifies applicable PIL legislation (such as Switzerland's PILA), international conventions, and relevant case precedents. Output format is an ordered list by relevance, or ["NA"] if no provisions are found. Verify that cited provisions are accurate and properly prioritized for the specific choice of law issues present.

**Choice of Law Issue**: Formulation of the central PIL question as a generalizable yes-no question that extends beyond case-specific details. The issue should capture the underlying choice of law principle that could apply to similar cases. Edit to ensure the issue is precisely framed and legally significant.

**Court's Position**: Summary of how the court resolved the choice of law issue, presented as a generalizable principle applicable to similar cases. This integrates all previous analysis components and should directly answer the identified choice of law issue. Focus on the legal reasoning and principles rather than case-specific outcomes.

## Expert Interaction and Quality Control

Each analysis step requires expert evaluation through a 0-100 scoring system followed by a manuak editing step, which can be used to make any modifications necessary. The system maintains chronological history of all interactions, clearly distinguishing between AI outputs (displayed with gray background) and user inputs (displayed with purple background).

Provide specific, actionable feedback when requesting improvements. Focus on legal precision, proper terminology, and jurisdiction-specific frameworks. Take advantage of iterative refinement - multiple feedback rounds often yield better results than single attempts.

For editing, the text areas are pre-populated with current AI output. Make comprehensive edits to ensure professional quality before advancing to the next step. Changes are immediately incorporated into the system's context for subsequent analysis.

## Technical Considerations and Best Practices

The system can process PDF files directly or use raw text provided by the user. Ensure complete court decision text is provided, as incomplete input affects all subsequent analysis. The system works with multiple input languages but produces English output with proper legal terminology.

Analysis state is maintained throughout the session but lost if the browser session ends unexpectedly. Complete the full analysis in a single session when possible. Use "Clear History" to reset and start a new case analysis. For optimal results, prepare by reviewing the case beforehand and formulating preliminary opinions about appropriate answers for each analysis category. This enables more effective evaluation and editing of AI outputs. Results are automatically saved to the database upon completion of all analysis steps, including user identification, model used, case citation, and complete analysis state with timestamps. The system provides a completion message with links to the broader CoLD project resources.

The analyzer integrates with the broader CoLD project workflow where legal specialists access court decisions through NocoDB, extract full text from various sources, and use this tool for systematic PIL analysis. The structured output supports comparative research and contributes to the CoLD database of analyzed cases.