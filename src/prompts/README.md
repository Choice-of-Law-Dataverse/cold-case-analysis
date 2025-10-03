# CoLD Case Analyzer - Prompts Documentation

This document contains all prompts used by the CoLD Case Analyzer system, organized by category and jurisdiction.

**⚠️ Note:** The CoLD Case Analyzer can make mistakes. Please review each answer carefully.



## Table of Contents

- [System-Level Prompts](#system-level-prompts)

- [Jurisdiction-Specific Prompts](#jurisdiction-specific-prompts)

  - [Civil Law Jurisdiction](#civil-law-jurisdiction)

  - [Common Law Jurisdiction](#common-law-jurisdiction)

  - [India Jurisdiction](#india-jurisdiction)



## System-Level Prompts

These prompts are used for initial system classification and are applied regardless of jurisdiction.

### Legal System Type Detection

*File: `legal_system_type_detection.py`*


#### Legal System Type Detection

```text
You are an expert legal scholar with deep knowledge of comparative legal systems worldwide. Your task is to analyze the provided text and classify it according to the legal system tradition it represents.

**CRITICAL INSTRUCTION: The jurisdiction name provided is HIGHLY RELIABLE and should take precedence over textual ambiguities.**

**CLASSIFICATION TASK:**
Determine if the text is from a:
1. "Civil-law jurisdiction" - Legal systems based on comprehensive written codes (Romano-Germanic tradition)
2. "Common-law jurisdiction" - Legal systems based on judicial precedents and case law (Anglo-American tradition) 
3. "No court decision" - Text that is not a judicial decision or cannot be classified

**ANALYSIS FRAMEWORK:**

**STEP 1: JURISDICTION-BASED CLASSIFICATION (PRIMARY)**
The provided jurisdiction is: {jurisdiction_name}

**Known Civil-Law Jurisdictions Include:**
- Switzerland, Germany, France, Italy, Spain, Austria, Netherlands, Belgium, Portugal, Greece
- Nordic countries: Finland, Sweden, Denmark, Norway, Iceland  
- Eastern Europe: Poland, Czech Republic, Slovakia, Hungary, Romania, Bulgaria, Croatia, Slovenia
- Baltic states: Estonia, Latvia, Lithuania
- Asia: Japan, South Korea, China, Taiwan, Thailand, Vietnam, Indonesia
- Latin America: Brazil, Argentina, Mexico, Chile, Colombia, Peru, Ecuador, Bolivia, Paraguay
- Middle East: Turkey, Egypt, Iran, Lebanon, Jordan, Kuwait, Qatar, UAE, Saudi Arabia
- Africa: Tunisia, Morocco, Algeria, Ethiopia, Angola, Mozambique
- Russia, Ukraine, and former Soviet states

**Known Common-Law Jurisdictions Include:**
- United States, United Kingdom (England, Scotland, Wales, Northern Ireland), Ireland
- Commonwealth: Canada, Australia, New Zealand, India, Pakistan, Bangladesh, Sri Lanka
- Southeast Asia: Malaysia, Singapore, Hong Kong, Philippines
- Africa: South Africa, Nigeria, Ghana, Kenya, Uganda, Tanzania, Zambia, Zimbabwe
- Caribbean: Jamaica, Barbados, Trinidad and Tobago, Bahamas, Belize

**STEP 2: TEXTUAL ANALYSIS (SECONDARY)**
Only if jurisdiction is unknown or ambiguous, examine text for:

**Civil-law indicators:**
- References to codes, statutes (e.g., "Article 123", "§ 242 BGB", "Code Civil")
- Systematic application of written law without extensive case citations
- Formal, deductive reasoning from general principles
- Court names: Bundesgerichtshof, Tribunal Federal, Cour de Cassation, Tribunal Supremo
- Swiss-specific: References to "Swiss Federal Act on Private International Law (PILA)", "Bundesgericht", "Tribunal fédéral"

**Common-law indicators:**
- Extensive case law citations with case names and years
- Reasoning through precedent and analogy ("distinguishing", "following")
- Terms: "plaintiff," "defendant," "holding," "ratio decidendi"
- Case styling: "[Name] v. [Name]"
- Court names: Supreme Court, Court of Appeals, High Court

**IMPORTANT NOTES:**
- Swiss court decisions are often published in English but Switzerland is definitively a CIVIL LAW jurisdiction
- Many civil law countries publish decisions in English for international accessibility
- Language alone should never override jurisdiction-based classification
- When jurisdiction clearly indicates one system but text suggests another, trust the jurisdiction

**OUTPUT REQUIREMENTS:**
Respond with exactly one of these phrases:
- Civil-law jurisdiction
- Common-law jurisdiction  
- No court decision

**TEXT TO ANALYZE:**
{text}
```

### Precise Jurisdiction Detection Prompt

*File: `precise_jurisdiction_detection_prompt.py`*


#### Precise Jurisdiction Detection

```text
You are a world-class legal expert specializing in identifying court jurisdictions from court decisions and legal documents.

Your task is to analyze the following court decision text and identify the PRECISE jurisdiction where this court decision was issued.

AVAILABLE JURISDICTIONS:
{jurisdiction_list}

ANALYSIS GUIDELINES:
Look for the following key indicators in the text:

1. **Court Names**: 
   - Supreme courts, constitutional courts, high courts, appellate courts
   - Administrative courts, commercial courts, specialized tribunals
   - Federal vs. state/provincial court indicators

2. **Legal References**:
   - Specific statutes, codes, or legal frameworks cited
   - Constitutional provisions or articles referenced
   - Legal precedents or case law cited

3. **Geographic and Administrative Indicators**:
   - City names, regional references
   - Government departments or agencies mentioned
   - Administrative districts or legal divisions

4. **Language and Legal Terminology**:
   - Language of the decision (original language)
   - Legal terminology specific to certain legal systems
   - Citation formats and legal conventions

5. **Case Citation Format**:
   - How cases are cited and numbered
   - Court reporting systems used
   - Date formats and legal citation styles

RESPONSE REQUIREMENTS:
- Identify the EXACT jurisdiction name from the provided list
- If uncertain, choose the most likely match and indicate lower confidence
- If no clear jurisdiction can be determined, respond with "Unknown"
- Provide clear reasoning for your identification

Respond in the following format:
/"Jurisdiction/"

COURT DECISION TEXT:
{text}
```

## Jurisdiction-Specific Prompts

These prompts are tailored for specific legal systems and jurisdictions.

## Civil Law Jurisdiction

### Col Section

*File: `civil_law\col_section_prompt.py`*


#### Col Section

```text
TASK: Extract all portions of the judgment that discuss choice of law in private international law (PIL) contexts.
INSTRUCTIONS:
1.	Scope of Extraction: Identify and extract the most important paragraphs, sentences, or sections where the court:
-	Determines the choice of law of the parties as per any rules of private international law
-	Discusses "applicable law," "proper law," "governing law," or "choice of law"
-	Analyzes party autonomy in law selection
-	Applies conflict of laws principles
-	References foreign legal systems in determining applicable law
-	Discusses the "closest connection" test or similar PIL methodologies
More specifically, when preparing the output, prioritize: (1) The court's direct conclusions about applicable law, (2) The court's reasoning about choice of law rules, (3) The court's analysis of contractual choice of law clauses, (4) The court's application of PIL principles.
1.1 Make sure to include the following parts:
-	The court's reasoning about law selection and analysis of party agreements on governing law
-	Discussion of PIL principles and application of foreign law provisions
-	Jurisdiction discussions ONLY when they directly involve choice of law analysis (e.g., determining which law governs the interpretation of jurisdiction clauses, or how choice of law affects jurisdictional determinations)
-	Supporting citations and precedents only when the court explicitly relies on them for its choice of law determination
1.2 Exclude all of the following:
-	Pure procedural matters unrelated to choice of law
-	Pure jurisdictional analysis that doesn't engage with PIL choice of law principles
-	Enforcement issues not touching on choice of law
-	Other matters on the merit of the dispute unrelated to choice of law or PIL
-	Lengthy quotes from cited cases unless the court explicitly adopts them as part of its analysis

2.	Extraction Method:
-	Reproduce the court's exact language using quotation marks, abbreviating text using brackets [...] when necessary
-	Extract complete sentences with essential context only
-	Focus primarily on the court's own reasoning and analysis
3.	Output Format:
[Section 1:] 
"[Exact court language]" 
[Section 2:] 
"[Exact court language]"
4.	Quality Check:
-	Ensure each extracted section shows the court's reasoning chain
-	Break longer passages into separate sections if they address different choice of law issues
-	If necessary, add brackets […] to abbreviate the text if it touches upon matters included in the exclusion list. 
5.	CONSTRAINT: Base extraction solely on the provided judgment text. Do not add interpretive commentary or external legal knowledge.”


Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
```

### Pil Theme

*File: `civil_law\pil_theme_prompt.py`*


#### Pil Theme

```text
Your task is to assign specific themes to a court decision. Your response consists of the most fitting value(s) from the "Keywords" column in the format "keyword". You assign the theme most closely related to the choice of law issue. For example, the decision might be about "Party autonomy", but the issue refers specifically to "Tacit choice". Be as precise as possible. THE OUTPUT HAS TO BE ONE OR MULTIPLE OF THE VALUES FROM THE TABLE. Your output should adhere to the following format:
["Theme 1", "Theme 2"]
If the decision goes beyond the scope of the predetermined themes, return ["NA"].
Here is the table with all keywords and their definitions:
{themes_table}

Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
{col_section}
```

### Analysiss

*File: `civil_law\analysis_prompts.py`*


#### Abstract

```text
TASK: Create a concise abstract summarizing this PIL case's choice of law analysis and outcome.
INSTRUCTIONS:
1.	Primary Approach: 
Synthesize a comprehensive abstract using the analytical components you have previously extracted from this judgment.
2.	Content Integration: Your abstract must incorporate: 
-	Essential facts establishing the PIL context
-	The choice of law issue(s) the court addressed
-	The court's position
3.	Structure Requirements: 
-	Write exactly one paragraph
-	Begin with the factual context that created the PIL issue
-	Progress through the legal question and court's reasoning
-	Conclude with the precedential principle established
4.	Writing Standards: 
-	Use clear, professional language
-	Maintain logical flow from facts to legal conclusion
-	Focus on PIL methodology and choice of law principles, not case-specific outcomes
-	Include sufficient detail for legal research purposes while remaining concise
5.  Fallback Instruction: 
If an official “abstract”, “headnote”/ “case note” exists in the judgment text, extract it instead of synthesizing. Please translate it into English and state that it is a verbatim translation.

6.	OUTPUT FORMAT:
A.	**ABSTRACT WHEN NOTHING IS AVAILABLE IN THE DECISION:**
[Single paragraph synthesizing facts, PIL issues, court's reasoning, and precedential outcome]
B.	**ABSTRACT WHEN A SUMMARY IS AVAILABLE IN THE DECISION:**
[Extracted and translated paragraph adding (verbatim) at the end].
- Use a maximum of 300 words.

7.	CONSTRAINT: Base the abstract on your previous analysis of this judgment's PIL components, ensuring it captures the essential choice of law elements for legal research and reference purposes. Use a maximum of four sentences.

Court Decision Text:
{text}

The private international law themes are:
{classification}

The relevant facts are:
{facts}

The private international law provisions are:
{pil_provisions}

The choice of law issue is:
{col_issue}

The court's position is:
{court_position}



The abstract is:
```

#### Col Issue

```text
Your task is to identify the main private international law issue from a court decision. Your response will be a concise question. Examples:
-	“Can the parties validly choose the law of a country with no connection to their contract?”
-	"Can an implied choice of law be inferred from forum selection clauses?"
-	"Does the closest connection test apply when parties made no express choice of law?"

The issue you extract will have to do with choice of law and the output has to be phrased in a general fashion. The issue is not about the specific details of the case but rather the overall choice-of-law issue behind the case. If any legal provisions are mentioned, use their English abbreviation.

The issue in this case is related to this theme/these themes:
{classification_definitions}

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

The issue is:
```

#### Courts Position

```text
Summarize the court's position on the choice-of-law issue(s) within the decision. Your response is phrased in a general way, generalizing the issue(s) so that your generalization could be applied to other private international law cases. If any legal provisions are mentioned, use their English abbreviation. Your output is a direct answer to the issue laid out here:
{col_issue}

CONSTRAINTS:
- Base the response on the provided judgment text and extracted sections only.
- Maintain a neutral and objective tone.
- Use a maximum of 300 words.

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

Classified Theme(s):
{classification}

The court's position is:
```

#### Facts

```text
TASK: Extract and synthesize factual elements essential for understanding the choice of law analysis into a single, coherent paragraph.
INSTRUCTIONS:
1.	Output Requirement: 
Provide an answer as concise as possible, up to 300 words containing all relevant facts in narrative form.
2.	Content Priority:
Elaborate on facts including, but not limited to the following, as long as they are relevant for the private international law (PIL) and choice of law discussion in the decision: 
-	Party characteristics (nationality, domicile, place of business/incorporation)
-	Nature and geography of the underlying transaction/relationship
-	Express or implied choice of law indicators
-	Specific circumstances that created the choice of law issue
3.	Writing Guidelines: 
-	Use flowing, connected sentences rather than listing facts in points
-	Employ transitional phrases to link different factual elements
-	Maintain chronological or logical progression 
-	Keep sentences concise but substantive
4.	Inclusion Standards: 
-	Include: Connecting factors, transactional geography, choice of law clauses, foreign law invocations, conflict triggers
-	Exclude: Specific amounts, exact dates, individual names, procedural details, unrelated contract terms
5.	OUTPUT FORMAT:
[Single paragraph containing all essential facts in narrative form, explaining the international elements and circumstances that necessitated choice of law analysis. MAXIMUM 300 WORDS.]
6.	CONSTRAINT:
Base the factual narrative solely on the provided judgment text, synthesizing information from both the full text and extracted choice of law section. Use a maximum of four sentences.

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

The facts are:
```

#### Pil Provisions

```text
Your task is to extract rules related to choice of law cited in a court decision. Your response is a list of provisions sorted by the impact of the rules for the choice of law issue(s) present within the court decision. Your response consists of this list only, no explanations or other additional information. A relevant provision usually stems from the most prominent legislation dealing with private international law in the respective jurisdiction. In some countries, the relevant provisions are included in the civil code. Other countries have acts that include private international law provisions. In many cases, the relevant provisions can also be found in international treaties. If no legislative provision is found, double-check whether there is any other court decision cited as a choice of law precedent.
OUTPUT FORMAT:
- The output adheres to this format: ["<provision>, <abbreviated name of the instrument>", "<provision>, <abbreviated name of the instrument>", ...]
- Example for Switzerland: ["Art. 187, PILA"]
- If you do not find PIL provisions in the court decision or if you are not sure, return ["NA"]. If any language other than English is used to cite a provision, use their English abbreviation.
LIMITATIONS:
- No literature or other doctrinal remarks
- Do not use the paragraph symbol (§). If necessary use the abbreviation "Para."

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

The private international law provisions are:
```

## Common Law Jurisdiction

### Col Section

*File: `common_law\col_section_prompt.py`*


#### Col Section

```text
TASK: Extract all portions of the judgment that discuss choice of law in private international law (PIL) contexts.
INSTRUCTIONS:
1.	Scope of Extraction: Identify and extract the most important paragraphs, sentences, or sections where the court:
-	Determines the choice of law of the parties as per any rules of private international law
-	Discusses "applicable law," "proper law," "governing law," or "choice of law"
-	Analyzes party autonomy in law selection
-	Applies conflict of laws principles
-	References foreign legal systems in determining applicable law
-	Discusses the "closest connection" test or similar PIL methodologies
More specifically, when preparing the output, prioritize: (1) The court's direct conclusions about applicable law, (2) The court's reasoning about choice of law rules, (3) The court's analysis of contractual choice of law clauses, (4) The court's application of PIL principles.
1.1 Make sure to include the following parts:
-	The court's reasoning about law selection and analysis of party agreements on governing law
-	Discussion of PIL principles and application of foreign law provisions
-	Both ratio decidendi and obiter dicta related to choice of law
-	Jurisdiction discussions ONLY when they directly involve choice of law analysis (e.g., determining which law governs the interpretation of jurisdiction clauses, or how choice of law affects jurisdictional determinations)
-	Supporting citations and precedents only when the court explicitly relies on them for its choice of law determination
1.2 Exclude all of the following:
-	Pure procedural matters unrelated to choice of law
-	Pure jurisdictional analysis that doesn't engage with PIL choice of law principles
-	Enforcement issues not touching on choice of law
-	Other matters on the merit of the dispute unrelated to choice of law or PIL
-	Lengthy quotes from cited cases unless the court explicitly adopts them as part of its analysis
2.	Extraction Method:
-	Reproduce the court's exact language using quotation marks, abbreviating text using brackets [...] when necessary
-	Extract complete sentences with essential context only
-	Focus primarily on the court's own reasoning and analysis
3.	Output Format:
[Section 1:] 
"[Exact court language]" 
[Section 2:] 
"[Exact court language]"
4.	Quality Check:
-	Ensure each extracted section shows the court's reasoning chain
-	Break longer passages into separate sections if they address different choice of law issues
-	If necessary, add brackets […] to abbreviate the text if it touches upon matters included in the exclusion list. 
5.	CONSTRAINT: Base extraction solely on the provided judgment text. Do not add interpretive commentary or external legal knowledge.”

Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
```

### Pil Theme

*File: `common_law\pil_theme_prompt.py`*


#### Pil Theme

```text
Your task is to assign specific themes to a court decision. Your response consists of the most fitting value(s) from the "Keywords" column in the format "keyword". You assign the theme most closely related to the choice of law issue. For example, the decision might be about "Party autonomy", but the issue refers specifically to "Tacit choice". Be as precise as possible. THE OUTPUT HAS TO BE ONE OR MULTIPLE OF THE VALUES FROM THE TABLE. Your output should adhere to the following format:
["Theme 1", "Theme 2"]
If the decision goes beyond the scope of the predetermined themes, return ["NA"].
Here is the table with all keywords and their definitions:
{themes_table}

Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
{col_section}
```

### Analysiss

*File: `common_law\analysis_prompts.py`*


#### Abstract

```text
TASK: Create a concise abstract summarizing this PIL case's choice of law analysis and outcome.
INSTRUCTIONS:
1.	Primary Approach: 
Synthesize a comprehensive abstract using the analytical components you have previously extracted from this judgment.
2.	Content Integration: Your abstract must incorporate: 
-	Essential facts establishing the PIL context
-	The choice of law issue(s) the court addressed
-	The court's ratio decidendi on applicable law
-	The legal outcome/conclusion
3.	Structure Requirements: 
-	Write exactly one paragraph
-	Begin with the factual context that created the PIL issue
-	Progress through the legal question and court's reasoning
-	Conclude with the precedential principle established
4.	Writing Standards: 
-	Use clear, professional language
-	Maintain logical flow from facts to legal conclusion
-	Focus on PIL methodology and choice of law principles, not case-specific outcomes
-	Include sufficient detail for legal research purposes while remaining concise
5.	Fallback Instruction: 
If an official “abstract”, “headnote”/”case note” exists in the judgment text, extract it instead of synthesizing.

6.	OUTPUT FORMAT:
A.	**ABSTRACT WHEN NOTHING IS AVAILABLE IN THE DECISION:**
[Single paragraph synthesizing facts, PIL issues, court's reasoning, and precedential outcome]
B.	**ABSTRACT WHEN A CASE NOTE IS AVAILABLE IN THE DECISION:**
[Extracted paragraph adding (verbatim) at the end].

7.	CONSTRAINT: Base the abstract on your previous analysis of this judgment's PIL components, ensuring it captures the essential choice of law elements for legal research and reference purposes.

Court Decision Text:
{text}

The private international law themes are:
{classification}

The relevant facts are:
{facts}

The private international law provisions are:
{pil_provisions}

The choice of law issue is:
{col_issue}

The court's position is (ratio decidendi):
{court_position}

The obiter dicta is:
{obiter_dicta}

The dissenting opinions are:
{dissenting_opinions}



The abstract is:
```

#### Col Issue

```text
TASK: Identify the specific choice of law questions that the court actually decided in this private international law (PIL) case. 
INSTRUCTIONS:
1.	Issue Identification Criteria: 
Extract only questions about applicable law that the court explicitly or implicitly resolved to reach its decision. Focus on what the court needed to determine, not what parties argued or preliminary questions considered but not decided. If there is only one issue, then return only one question.
2.	Question Formulation: 
Frame each issue as a precise legal question. Examples:
-	“Can the parties validly choose the law of a country with no connection to their contract?”
-	"Can an implied choice of law be inferred from forum selection clauses?"
-	"Does the closest connection test apply when parties made no express choice of law?"
3.	Scope Guidelines: 
-	Include: Questions about validity of express choices, methods for determining implied choices, default rules in absence of choice, scope of chosen law, renvoi issues
-	Include: Issues about connecting factors, party autonomy limitations, public policy exceptions
-	Exclude: Pure jurisdictional questions, procedural law issues, enforcement matters unrelated to choice of law
4.	Output Requirements: 
-	Return a concise question. Only if the choice of law issues present in the case thematically exceed the possibility of phrasing it in one single questions, return more.
-	Use precise, legally accurate terminology
-	Ensure each question reflects a choice of law determination actually made by the court
5.	Quality Check: Each identified issue should be answerable by pointing to specific court reasoning in the choice of law analysis.
6.   CONSTRAINT: Base issue identification solely on the court's actual analysis and resolution, drawing from both the full judgment text and extracted choice of law section.

The issue in this case is related to this theme/these themes:
{classification_definitions}

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

The issue is:
```

#### Courts Position Dissenting Opinions

```text
TASK: Identify and summarize any dissenting or minority judicial opinions specifically related to choice of law analysis.
INSTRUCTIONS:
1.	Scope of Analysis: 
-	Focus only on disagreements about private international law (PIL) methodology, choice of law principles, or applicable law determination
-	Exclude dissents on unrelated procedural, jurisdictional, or substantive law matters
-	Include concurring opinions that reach the same result through different PIL reasoning
2.	Content Extraction: 
-	Judge's name/designation (if provided)
-	Core PIL disagreement with the majority approach
-	Alternative choice of law methodology or principle proposed
-	Different conclusion about applicable law (if any)
3.	Analysis Requirements: 
-	Distinguish between methodological disagreements (how to determine applicable law) and application disagreements (which law applies)
-	Focus on legal reasoning differences and methodological disagreements, not factual disputes
-	Capture the essence of alternative PIL approaches suggested
4.	Output Standards: 
-	Provide concise but complete summary of each dissenting PIL position
-	If multiple dissents exist, address each separately
-	If partial agreement exists, specify areas of PIL agreement vs. disagreement
5.	OUTPUT FORMAT:
[Judge name (if provided)]: [Summary of PIL disagreement and alternative approach]
OR
"No dissenting opinion or minority opinion on the choice of law issue."
6.	CONSTRAINT: Extract only from the provided judgment text, focusing exclusively on choice of law disagreements while ignoring dissents on other legal issues.

Your output is a direct answer to the issue laid out here:
{col_issue}

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

Classified Theme(s):
{classification}

The dissenting opinions are:
```

#### Courts Position Obiter Dicta

```text
TASK: Extract judicial observations about choice of law that are not essential to the court's decision but provide persuasive legal commentary.
INSTRUCTIONS:
1.	Obiter Identification Method: 
-	Apply the inversion test: Could the court have reached the same decision if this statement were omitted or reversed?
-	If yes, the statement is obiter dicta
-	Focus on legal propositions, principles, or methodological observations, not factual findings
2.	PIL-Relevant Obiter Categories: 
-	Alternative choice of law approaches the court considered but didn't apply
-	Comparative observations about foreign private international law (PIL) systems or practices
-	Commentary on the development or future direction of PIL
-	Hypothetical scenarios or broader applications beyond the case facts
-	Judicial observations about PIL methodology or theoretical frameworks
-	Commentary on party autonomy principles not directly applied
3.	Content Requirements: 
-	Include only substantive legal observations, not casual remarks or procedural comments
-	Extract statements that could influence future PIL reasoning, even if not binding
-	Focus on the court's legal analysis, not factual characterizations or case-specific applications
-	Exclude pure policy discussions unless they contain legal principles
4.	Output Specifications: 
-	Present each obiter observation clearly and concisely
-	Use the court's language where possible, but may paraphrase for clarity
-	If no relevant obiter exists, state: "No obiter dicta on choice of law issues identified"
-	Organize multiple obiter statements logically (by topic or sequence in judgment)
-   Use a maximum of 300 words in total
-   Do not include unnecessary titles, use only verbatim quotations, and do not display inversion test reasoning
5.	OUTPUT FORMAT:
[Legal observation 1 - court's non-essential commentary on PIL/choice of law]

[Legal observation 2 - if applicable]
6.	CONSTRAINT: Extract only judicial commentary from the provided judgment text that relates to PIL methodology or choice of law principles but was not necessary for the court's actual decision.

Your output is a direct answer to the issue laid out here:
{col_issue}

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

Classified Theme(s):
{classification}

The obiter dicta is:
```

#### Courts Position

```text
TASK: Extract the binding legal principle(s) that the court established as essential to its choice of law decision.
INSTRUCTIONS:
1.	Ratio Identification Method: 
-	Identify each legal proposition the court stated regarding choice of law
-	Apply the inversion test mentally: Would reversing this proposition change the court's conclusion?
-	Include only propositions where the answer is "no" - these are ratio decidendi
2.	Content Requirements: 
-	Extract the court's binding legal rule(s), not factual findings or case-specific applications
-	State each principle as a clear, precedential rule applicable to future cases
-	Focus on private international law (PIL) methodology, not the specific contractual or factual outcome
-	Use the court's own formulation where possible, condensed into the form of a principle.
3.	Output Specifications: 
-	State each ratio as a complete legal principle in 1-2 sentences maximum
-	If multiple ratios exist on different choice of law points, number them separately
-	Ensure each principle directly addresses the legal issue(s) previously identified
-	Avoid factual details, policy reasoning, or persuasive commentary
4.	Quality Standards: 
-	Each ratio should be actionable as precedent in future PIL cases
-	Principles should be neither too narrow (case-specific) nor too broad (unhelpful generalization)
-	Focus on what the court held must be done, not what it suggested or considered
5.	OUTPUT FORMAT:
[Legal principle 1 - complete rule in 1-2 sentences]
[Legal principle 2 - if applicable]
6.	CONSTRAINT: Extract principles solely from the court's binding determinations in the provided judgment text, ensuring each principle was necessary for the court's choice of law conclusion.

Your output is a direct answer to the issue laid out here:
{col_issue}

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

Classified Theme(s):
{classification}

The court's position is:
```

#### Facts

```text
TASK: Extract and synthesize factual elements essential for understanding the choice of law analysis into a single, coherent paragraph.
INSTRUCTIONS:
1.	Output Requirement: 
Provide an answer as concise as possible, up to 300 words containing all relevant facts in narrative form.
2.	Content Priority:
Elaborate on facts including, but not limited to the following, as long as they are relevant for the private international law (PIL) and choice of law discussion in the decision: 
-	Party characteristics (nationality, domicile, place of business/incorporation)
-	Nature and geography of the underlying transaction/relationship
-	Express or implied choice of law indicators
-	Specific circumstances that created the choice of law issue
3.	Writing Guidelines: 
-	Use flowing, connected sentences rather than listing facts in points
-	Employ transitional phrases to link different factual elements
-	Maintain chronological or logical progression 
-	Keep sentences concise but substantive
4.	Inclusion Standards: 
-	Include: Connecting factors, transactional geography, choice of law clauses, foreign law invocations, conflict triggers
-	Exclude: Specific amounts, exact dates, individual names, procedural details, unrelated contract terms, conclusion of the case
5.	OUTPUT FORMAT:
[Single paragraph containing all essential facts in narrative form, explaining the international elements and circumstances that necessitated choice of law analysis. MAXIMUM 300 WORDS.]
6.	CONSTRAINT:
Base the factual narrative solely on the provided judgment text, synthesizing information from both the full text and extracted choice of law section.

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

The facts are:
```

#### Pil Provisions

```text
TASK: Extract only the legal authorities that the court actually used to support its choice of law reasoning and decision.
INSTRUCTIONS:
1.	Inclusion Standard: Include authorities only where the court: 
-	Applied the authority's principle to reach its conclusion
-	Adopted the authority's reasoning as part of its analysis
-	Used the authority to interpret or clarify legal principles
-	Distinguished or followed the authority's approach
-	If no textbooks/academic sources, and/or statutory provisions have been cited, then do not output these headings.
2.	Authority Categories: 
-	Judicial Decisions: Cases the court followed, distinguished, or applied
-	Textbooks/Treatises: Academic sources (Dicey, Cheshire, etc.) the court cited for legal principles
-	Statutory Provisions: Specific legislative rules the court applied
-	Legal Principles: Established doctrines or tests the court referenced.
3.	Usage Description Requirements: 
-	For Cases: List case name only. Include citations only if provided in the judgment. (no usage explanation needed)
-	For Textbooks/Academic Sources: List names. Provide one-line explanation of how used for each.
-	For Statutory Provisions: List provision only (no usage explanation needed)
4.	Exclusions: 
-	Authorities cited by parties/counsel unless court adopted their reasoning
-	Cases mentioned for historical context without direct application
-	Authorities cited but not used in the court's actual reasoning
-	General legal background citations not supporting the specific decision
-   Sources that do not have precedential value
5.	OUTPUT FORMAT:
**Judicial Precedents:**
-	[Case name 1]
-	[Case name 2]
**Textbooks/Academic Sources:**
-	[Source]: [Brief explanation of how court used it]
**Statutory Provisions:**
-	[Provision name/section]
6.	CONSTRAINT: Extract only from the court's own reasoning in the provided judgment text, focusing on authorities that directly supported the choice of law analysis and conclusion.

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

The authorities are:
```

## India Jurisdiction

### Col Section

*File: `india\col_section_prompt.py`*


#### Col Section

```text
TASK: Extract all portions of the judgment that discuss choice of law in private international law (PIL) contexts.
INSTRUCTIONS:
1.	Scope of Extraction: Identify and extract the most important paragraphs, sentences, or sections where the court:
-	Determines the choice of law of the parties as per any rules of private international law
-	Discusses "applicable law," "proper law," "governing law," or "choice of law"
-	Analyzes party autonomy in law selection
-	Applies conflict of laws principles
-	References foreign legal systems in determining applicable law
-	Discusses the "closest connection" test or similar PIL methodologies
More specifically, when preparing the output, prioritize: (1) The court's direct conclusions about applicable law, (2) The court's reasoning about choice of law rules, (3) The court's analysis of contractual choice of law clauses, (4) The court's application of PIL principles.
1.1 Make sure to include the following parts:
-	The court's reasoning about law selection and analysis of party agreements on governing law
-	Discussion of PIL principles and application of foreign law provisions
-	Both ratio decidendi and obiter dicta related to choice of law
-	Jurisdiction discussions ONLY when they directly involve choice of law analysis (e.g., determining which law governs the interpretation of jurisdiction clauses, or how choice of law affects jurisdictional determinations)
-	Supporting citations and precedents only when the court explicitly relies on them for its choice of law determination
1.2 Exclude all of the following:
-	Pure procedural matters unrelated to choice of law
-	Pure jurisdictional analysis that doesn't engage with PIL choice of law principles
-	Enforcement issues not touching on choice of law
-	Other matters on the merit of the dispute unrelated to choice of law or PIL
-	Lengthy quotes from cited cases unless the court explicitly adopts them as part of its analysis

2.	Extraction Method:
-	Reproduce the court's exact language using quotation marks, abbreviating text using brackets [...] when necessary
-	Extract complete sentences with essential context only
-	Focus primarily on the court's own reasoning and analysis
3.	Output Format:
[Section 1:] 
"[Exact court language]" 
[Section 2:] 
"[Exact court language]"
4.	Quality Check:
-	Ensure each extracted section shows the court's reasoning chain
-	Break longer passages into separate sections if they address different choice of law issues
-	If necessary, add brackets […] to abbreviate the text if it touches upon matters included in the exclusion list. 
5.	CONSTRAINT: Base extraction solely on the provided judgment text. Do not add interpretive commentary or external legal knowledge.”

Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
```

### Pil Theme

*File: `india\pil_theme_prompt.py`*


#### Pil Theme

```text
Your task is to assign specific themes to a court decision. Your response consists of the most fitting value(s) from the "Keywords" column in the format "keyword". You assign the theme most closely related to the choice of law issue. For example, the decision might be about "Party autonomy", but the issue refers specifically to "Tacit choice". Be as precise as possible. THE OUTPUT HAS TO BE ONE OR MULTIPLE OF THE VALUES FROM THE TABLE. Your output should adhere to the following format:
["Theme 1", "Theme 2"]
If the decision goes beyond the scope of the predetermined themes, return ["NA"].
Here is the table with all keywords and their definitions:
{themes_table}

Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
{col_section}
```

### Analysiss

*File: `india\analysis_prompts.py`*


#### Abstract

```text
TASK: Create a concise abstract summarizing this PIL case's choice of law analysis and outcome.
INSTRUCTIONS:
1.	Primary Approach: 
Synthesize a comprehensive abstract using the analytical components you have previously extracted from this judgment.
2.	Content Integration: Your abstract must incorporate: 
-	Essential facts establishing the PIL context
-	The choice of law issue(s) the court addressed
-	The court's ratio decidendi on applicable law
-	The legal outcome/conclusion
3.	Structure Requirements: 
-	Write exactly one paragraph
-	Begin with the factual context that created the PIL issue
-	Progress through the legal question and court's reasoning
-	Conclude with the precedential principle established
4.	Writing Standards: 
-	Use clear, professional language
-	Maintain logical flow from facts to legal conclusion
-	Focus on PIL methodology and choice of law principles, not case-specific outcomes
-	Include sufficient detail for legal research purposes while remaining concise
5.	Fallback Instruction: 
If an official “abstract”, “headnote”/”case note” exists in the judgment text, extract it instead of synthesizing.

6.	OUTPUT FORMAT:
A.	**ABSTRACT WHEN NOTHING IS AVAILABLE IN THE DECISION:**
[Single paragraph synthesizing facts, PIL issues, court's reasoning, and precedential outcome]
B.	**ABSTRACT WHEN A CASE NOTE IS AVAILABLE IN THE DECISION:**
[Extracted paragraph adding (verbatim) at the end].

7.	CONSTRAINT: Base the abstract on your previous analysis of this judgment's PIL components, ensuring it captures the essential choice of law elements for legal research and reference purposes.

Court Decision Text:
{text}

The private international law themes are:
{classification}

The relevant facts are:
{facts}

The private international law provisions are:
{pil_provisions}

The choice of law issue is:
{col_issue}

The court's position is (ratio decidendi):
{court_position}

The obiter dicta is:
{obiter_dicta}

The dissenting opinions are:
{dissenting_opinions}



The abstract is:
```

#### Col Issue

```text
TASK: Identify the specific choice of law questions that the court actually decided in this private international law (PIL) case. 
INSTRUCTIONS:
1.	Issue Identification Criteria: 
Extract only questions about applicable law that the court explicitly or implicitly resolved to reach its decision. Focus on what the court needed to determine, not what parties argued or preliminary questions considered but not decided. If there is only one issue, then return only one question.
2.	Question Formulation: 
Frame each issue as a precise legal question using "Whether..." format. Examples: 
-	"Whether parties can validly choose the law of a country with no connection to their contract?"
-	"Whether implied choice of law can be inferred from forum selection clauses?"
-	"Whether the closest connection test applies when parties made no express choice of law?"
-	"Whether Indian courts should apply foreign law to determine contractual validity?"
3.	Scope Guidelines: 
-	Include: Questions about validity of express choices, methods for determining implied choices, default rules in absence of choice, scope of chosen law, renvoi issues
-	Include: Issues about connecting factors, party autonomy limitations, public policy exceptions
-	Exclude: Pure jurisdictional questions, procedural law issues, enforcement matters unrelated to choice of law
4.	Output Requirements: 
-	Return a concise question. Only if the choice of law issues present in the case thematically exceed the possibility of phrasing it in one single questions, return more.
-	Use precise, legally accurate terminology
-	Ensure each question reflects a choice of law determination actually made by the court
-	Order issues from primary to secondary based on their importance to the court's reasoning
5.	Quality Check: Each identified issue should be answerable by pointing to specific court reasoning in the choice of law analysis.
6.	OUTPUT FORMAT:
1. Whether [specific choice of law question court resolved]
2. Whether [additional issue if present]
7.   CONSTRAINT: Base issue identification solely on the court's actual analysis and resolution, drawing from both the full judgment text and extracted choice of law section.

The issue in this case is related to this theme/these themes:
{classification_definitions}

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

The issue is:
```

#### Courts Position Dissenting Opinions

```text
TASK: Identify and summarize any dissenting or minority judicial opinions specifically related to choice of law analysis.
INSTRUCTIONS:
1.	Scope of Analysis: 
-	Focus only on disagreements about private international law (PIL) methodology, choice of law principles, or applicable law determination
-	Exclude dissents on unrelated procedural, jurisdictional, or substantive law matters
-	Include concurring opinions that reach the same result through different PIL reasoning
2.	Content Extraction: 
-	Judge's name/designation (if provided)
-	Core PIL disagreement with the majority approach
-	Alternative choice of law methodology or principle proposed
-	Different conclusion about applicable law (if any)
3.	Analysis Requirements: 
-	Distinguish between methodological disagreements (how to determine applicable law) and application disagreements (which law applies)
-	Focus on legal reasoning differences and methodological disagreements, not factual disputes
-	Capture the essence of alternative PIL approaches suggested
4.	Output Standards: 
-	Provide concise but complete summary of each dissenting PIL position
-	If multiple dissents exist, address each separately
-	If partial agreement exists, specify areas of PIL agreement vs. disagreement
5.	OUTPUT FORMAT:
[Judge name (if provided)]: [Summary of PIL disagreement and alternative approach]
OR
"No dissenting opinion or minority opinion on the choice of law issue."
6.	CONSTRAINT: Extract only from the provided judgment text, focusing exclusively on choice of law disagreements while ignoring dissents on other legal issues.

Your output is a direct answer to the issue laid out here:
{col_issue}

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

Classified Theme(s):
{classification}

The dissenting opinions are:
```

#### Courts Position Obiter Dicta

```text
TASK: Extract judicial observations about choice of law that are not essential to the court's decision but provide persuasive legal commentary.
INSTRUCTIONS:
1.	Obiter Identification Method: 
-	Apply the inversion test: Could the court have reached the same decision if this statement were omitted or reversed?
-	If yes, the statement is obiter dicta
-	Focus on legal propositions, principles, or methodological observations, not factual findings
2.	PIL-Relevant Obiter Categories: 
-	Alternative choice of law approaches the court considered but didn't apply
-	Comparative observations about foreign private international law (PIL) systems or practices
-	Commentary on the development or future direction of Indian PIL
-	Hypothetical scenarios or broader applications beyond the case facts
-	Judicial observations about PIL methodology or theoretical frameworks
-	Commentary on party autonomy principles not directly applied
3.	Content Requirements: 
-	Include only substantive legal observations, not casual remarks or procedural comments
-	Extract statements that could influence future PIL reasoning, even if not binding
-	Focus on the court's legal analysis, not factual characterizations or case-specific applications
-	Exclude pure policy discussions unless they contain legal principles
4.	Output Specifications: 
-	Present each obiter observation clearly and concisely
-	Use the court's language where possible, but may paraphrase for clarity
-	If no relevant obiter exists, state: "No obiter dicta on choice of law issues identified"
-	Organize multiple obiter statements logically (by topic or sequence in judgment)
-   Use a maximum of 300 words in total
-   Do not include unnecessary titles, use only verbatim quotations, and do not display inversion test reasoning
5.	OUTPUT FORMAT:
[Legal observation 1 - court's non-essential commentary on PIL/choice of law]

[Legal observation 2 - if applicable]
6.	CONSTRAINT: Extract only judicial commentary from the provided judgment text that relates to PIL methodology or choice of law principles but was not necessary for the court's actual decision.

Your output is a direct answer to the issue laid out here:
{col_issue}

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

Classified Theme(s):
{classification}

The obiter dicta is:
```

#### Courts Position

```text
TASK: Extract the binding legal principle(s) that the court established as essential to its choice of law decision.
INSTRUCTIONS:
1.	Ratio Identification Method: 
-	Identify each legal proposition the court stated regarding choice of law
-	Apply the inversion test mentally: Would reversing this proposition change the court's conclusion?
-	Include only propositions where the answer is "no" - these are ratio decidendi
2.	Content Requirements: 
-	Extract the court's binding legal rule(s), not factual findings or case-specific applications
-	State each principle as a clear, precedential rule applicable to future cases
-	Focus on private international law (PIL) methodology, not the specific contractual or factual outcome
-	Use the court's own formulation where possible, condensed into the form of a principle.
3.	Output Specifications: 
-	State each ratio as a complete legal principle in 1-2 sentences maximum
-	If multiple ratios exist on different choice of law points, number them separately
-	Ensure each principle directly addresses the legal issue(s) previously identified
-	Avoid factual details, policy reasoning, or persuasive commentary
4.	Quality Standards: 
-	Each ratio should be actionable as precedent in future PIL cases
-	Principles should be neither too narrow (case-specific) nor too broad (unhelpful generalization)
-	Focus on what the court held must be done, not what it suggested or considered
5.	OUTPUT FORMAT:
[Legal principle 1 - complete rule in 1-2 sentences]
[Legal principle 2 - if applicable]
6.	CONSTRAINT: Extract principles solely from the court's binding determinations in the provided judgment text, ensuring each principle was necessary for the court's choice of law conclusion.

Your output is a direct answer to the issue laid out here:
{col_issue}

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

Classified Theme(s):
{classification}

The court's position is:
```

#### Facts

```text
TASK: Extract and synthesize factual elements essential for understanding the choice of law analysis into a single, coherent paragraph.
INSTRUCTIONS:
1.	Output Requirement: 
Provide an answer as concise as possible, up to 300 words containing all relevant facts in narrative form.
2.	Content Priority:
Elaborate on facts including, but not limited to the following, as long as they are relevant for the private international law (PIL) and choice of law discussion in the decision: 
-	Party characteristics (nationality, domicile, place of business/incorporation)
-	Nature and geography of the underlying transaction/relationship
-	Express or implied choice of law indicators
-	Specific circumstances that created the choice of law issue
3.	Writing Guidelines: 
-	Use flowing, connected sentences rather than listing facts in points
-	Employ transitional phrases to link different factual elements
-	Maintain chronological or logical progression 
-	Keep sentences concise but substantive
4.	Inclusion Standards: 
-	Include: Connecting factors, transactional geography, choice of law clauses, foreign law invocations, conflict triggers
-	Exclude: Specific amounts, exact dates, individual names, procedural details, unrelated contract terms, conclusion of the case
5.	OUTPUT FORMAT:
[Single paragraph containing all essential facts in narrative form, explaining the international elements and circumstances that necessitated choice of law analysis. MAXIMUM 300 WORDS.]
6.	CONSTRAINT:
Base the factual narrative solely on the provided judgment text, synthesizing information from both the full text and extracted choice of law section.

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

The facts are:
```

#### Pil Provisions

```text
TASK: Extract only the legal authorities that the court actually used to support its choice of law reasoning and decision.
INSTRUCTIONS:
1.	Inclusion Standard: Include authorities only where the court: 
-	Applied the authority's principle to reach its conclusion
-	Adopted the authority's reasoning as part of its analysis
-	Used the authority to interpret or clarify legal principles
-	Distinguished or followed the authority's approach
-	If no textbooks/academic sources, and/or statutory provisions have been cited, then do not output these headings.
2.	Authority Categories: 
-	Judicial Decisions: Indian and foreign cases the court followed, distinguished, or applied
-	Textbooks/Treatises: Academic sources (Dicey, Cheshire, etc.) the court cited for legal principles
-	Statutory Provisions: Specific legislative rules the court applied
-	Legal Principles: Established doctrines or tests the court referenced.
3.	Usage Description Requirements: 
-	For Cases: List case name only. Include citations only if provided in the judgment. (no usage explanation needed)
-	For Textbooks/Academic Sources: List names. Provide one-line explanation of how used for each.
-	For Statutory Provisions: List provision only (no usage explanation needed)
4.	Exclusions: 
-	Authorities cited by parties/counsel unless court adopted their reasoning
-	Cases mentioned for historical context without direct application
-	Authorities cited but not used in the court's actual reasoning
-	General legal background citations not supporting the specific decision
-   Sources that do not have precedential value
5.	OUTPUT FORMAT:
**Judicial Precedents:**
-	[Case name 1]
-	[Case name 2]
**Textbooks/Academic Sources:**
-	[Source]: [Brief explanation of how court used it]
**Statutory Provisions:**
-	[Provision name/section]
6.	CONSTRAINT: Extract only from the court's own reasoning in the provided judgment text, focusing on authorities that directly supported the choice of law analysis and conclusion.

Court Decision Text:
{text}

Extracted Choice of Law Section:
{col_section}

The authorities are:
```
