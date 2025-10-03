# tests/test_pil_handler.py - Quick test for PIL provisions handler
import sys
from pathlib import Path

# Add the parent directory (streamlit) to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.pil_provisions_handler import format_pil_for_display, parse_pil_provisions

# Test with the example content
test_content = """**Judicial Precedents:**
- Shamil Bank of Bahrain EC v Beximco Pharmaceuticals Ltd

**Textbooks/Academic Sources:**
- Dicey, Morris & Collins: Used extensively to interpret the conflict rules under the Rome Convention, particularly regarding the recognition of foreign laws such as Jewish law and rules of incorporation, and to explain how law of a country is the relevant legal system in conflict of laws.
- Professor Burrows: Cited to discuss the modern approach to rescission for duress and the notion that counter-restitution can be flexible or monetary, influencing the court's understanding of the legal principles applicable to duress and mistake.
- Lord Diplock in Amin Rasheed Shipping Corp v Kuwait Insurance Co: Cited to support the principle that the choice of law in a contract involves law of a country, not non-national systems like general principles or lex mercatoria.
- Lord Blackburn in Erlanger v New Sombrero Phosphate: Cited regarding the principle that counter-restitution is generally required to rescind a contract, informing the court's approach to restitutio in integrum.

**Statutory Provisions:**
- Contracts (Applicable Law) Act 1990, Sections 2 and 3: Cited to interpret the application of the Rome Convention and conflict of laws rules regarding express and implied choice of law, and the applicable rules when no choice is made.
- Rome Convention, Articles 1, 3, 4, and 10: Cited in analyzing whether the parties' agreement pointed to Jewish law as the applicable law and how the Convention's rules influence the determination of the most closely connected law.
- Section 2(2) of the 1990 Act: Cited regarding the recognition of international conventions and their impact on conflict law.
- Arbitration Act 1996, Section 46: Cited concerning the tribunal's discretion to apply considerations, including law or principles not of a particular country, relevant to potential incorporation of Jewish law in arbitration.

**Legal Principles:**
- Principles from the Rome Convention/Regulation for determining the applicable law based on express, implied, or closest connection criteria.
- Doctrine that a choice of law must be certain, either expressly or impliedly, to be effective.
- Recognition that foreign legal systems, such as Jewish law, must be sufficiently identified and certain before they can be recognized as the applicable law of a contract.
- Doctrine that incorporation of foreign law provisions as contractual terms must be precise—general references or vague statements are insufficient.
- Principle that when no express or implied choice of law exists, the law most closely connected to the contract (e.g., the residence of the parties) applies.

**Summary of Court's Use of Authorities:**
The court relied on academic and statutory authorities to clarify conflict rules under the Rome Convention, particularly the requirements for a valid choice of law (certainty, express or implied) and the criteria for applying the law most closely connected. It also applied principles from key cases regarding the recognition of foreign law, incorporation as contractual terms, and the requirement of certainty in choice of law. The analysis clarified that Jewish law, while relevant as a legal system, cannot be recognized as the applicable law of the contract under existing conflict of laws principles because the parties' intent and the legal rules do not demonstrate a sufficiently certain express or implied choice."""

# Test parsing
parsed = parse_pil_provisions(test_content)
print("Parsed data:")
for key, value in parsed.items():
    print(f"{key}: {len(value) if isinstance(value, list) else 'text'}")

# Test formatting
formatted = format_pil_for_display(parsed)
print("\nFormatted output:")
print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
