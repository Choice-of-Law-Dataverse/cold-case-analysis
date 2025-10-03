#!/usr/bin/env python3
"""
Script to populate the prompts/README.md with all prompts found in the prompts subfolder.
Organizes prompts in a logical hierarchy for easy reference and documentation.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any


class PromptExtractor:
    """Extracts and organizes prompts from Python modules."""

    def __init__(self, prompts_dir: str):
        self.prompts_dir = Path(prompts_dir)
        self.base_module_name = "prompts"

    def load_module_from_file(self, file_path: Path) -> Any:
        """Dynamically load a Python module from file path."""
        try:
            spec = importlib.util.spec_from_file_location("temp_module", file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
        return None

    def extract_prompts_from_module(self, module: Any) -> dict[str, str]:
        """Extract all prompt variables from a module."""
        prompts = {}
        if not module:
            return prompts

        for attr_name in dir(module):
            if attr_name.endswith("_PROMPT") and not attr_name.startswith("_"):
                attr_value = getattr(module, attr_name)
                if isinstance(attr_value, str):
                    prompts[attr_name] = attr_value
        return prompts

    def get_all_prompt_files(self) -> list[Path]:
        """Get all Python files containing prompts."""
        prompt_files = []
        for file_path in self.prompts_dir.rglob("*.py"):
            if file_path.name != "__init__.py" and file_path.name != "populate_readme.py":
                prompt_files.append(file_path)
        return sorted(prompt_files)

    def organize_prompts(self) -> dict[str, Any]:
        """Organize all prompts by category and jurisdiction."""
        organized = {
            "system_prompts": {},
            "jurisdiction_prompts": {
                "civil_law": {},
                "common_law": {},
                "india": {}
            }
        }

        prompt_files = self.get_all_prompt_files()

        for file_path in prompt_files:
            relative_path = file_path.relative_to(self.prompts_dir)
            module = self.load_module_from_file(file_path)
            prompts = self.extract_prompts_from_module(module)

            if not prompts:
                continue

            # Categorize based on file location
            path_parts = relative_path.parts

            if len(path_parts) == 1:
                # Top-level files are system prompts
                organized["system_prompts"][file_path.stem] = {
                    "file_path": str(relative_path),
                    "prompts": prompts
                }
            elif len(path_parts) == 2 and path_parts[0] in ["civil_law", "common_law", "india"]:
                # Jurisdiction-specific prompts
                jurisdiction = path_parts[0]
                organized["jurisdiction_prompts"][jurisdiction][file_path.stem] = {
                    "file_path": str(relative_path),
                    "prompts": prompts
                }

        return organized


class MarkdownGenerator:
    """Generates markdown documentation from organized prompts."""

    def __init__(self):
        self.content = []

    def add_header(self, text: str, level: int = 1):
        """Add a markdown header."""
        self.content.append(f"{'#' * level} {text}\n")

    def add_text(self, text: str):
        """Add regular text."""
        self.content.append(f"{text}\n")

    def add_code_block(self, code: str, language: str = ""):
        """Add a code block."""
        self.content.append(f"```{language}\n{code}\n```\n")

    def add_prompt_section(self, prompt_name: str, prompt_content: str, level: int = 3):
        """Add a formatted prompt section."""
        # Clean up the prompt name for display
        display_name = prompt_name.replace("_PROMPT", "").replace("_", " ").title()

        self.add_header(f"{display_name}", level)

        # Extract the first few lines as description if they contain comments
        lines = prompt_content.strip().split("\n")
        description_lines = []
        prompt_lines = []

        in_description = True
        for line in lines:
            stripped = line.strip()
            if in_description and (stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''")):
                description_lines.append(stripped.lstrip("#").strip().strip('"""').strip("'''"))
            else:
                in_description = False
                prompt_lines.append(line)

        # Add description if found
        if description_lines:
            description = " ".join(description_lines).strip()
            if description:
                self.add_text(f"*{description}*\n")

        # Add the actual prompt content
        prompt_text = "\n".join(prompt_lines).strip()
        if prompt_text:
            self.add_code_block(prompt_text, "text")

    def generate_jurisdiction_section(self, jurisdiction: str, jurisdiction_data: dict[str, Any]):
        """Generate documentation for a specific jurisdiction."""
        jurisdiction_display = jurisdiction.replace("_", " ").title()
        self.add_header(f"{jurisdiction_display} Jurisdiction", 2)

        # Order analysis prompts logically
        prompt_order = [
            "col_section_prompt",
            "pil_theme_prompt",
            "analysis_prompts"
        ]

        for prompt_file in prompt_order:
            if prompt_file in jurisdiction_data:
                file_info = jurisdiction_data[prompt_file]
                file_display = prompt_file.replace("_", " ").title().replace(" Prompt", "")

                self.add_header(f"{file_display}", 3)
                self.add_text(f"*File: `{file_info['file_path']}`*\n")

                # Sort prompts within each file
                sorted_prompts = sorted(file_info["prompts"].items())
                for prompt_name, prompt_content in sorted_prompts:
                    self.add_prompt_section(prompt_name, prompt_content, 4)

    def generate_markdown(self, organized_prompts: dict[str, Any]) -> str:
        """Generate the complete markdown documentation."""
        # Header and introduction
        self.add_header("CoLD Case Analyzer - Prompts Documentation")
        self.add_text("This document contains all prompts used by the CoLD Case Analyzer system, organized by category and jurisdiction.")
        self.add_text("**⚠️ Note:** The CoLD Case Analyzer can make mistakes. Please review each answer carefully.")
        self.add_text("")

        # Table of Contents
        self.add_header("Table of Contents", 2)
        self.add_text("- [System-Level Prompts](#system-level-prompts)")
        self.add_text("- [Jurisdiction-Specific Prompts](#jurisdiction-specific-prompts)")
        self.add_text("  - [Civil Law Jurisdiction](#civil-law-jurisdiction)")
        self.add_text("  - [Common Law Jurisdiction](#common-law-jurisdiction)")
        self.add_text("  - [India Jurisdiction](#india-jurisdiction)")
        self.add_text("")

        # System-level prompts
        self.add_header("System-Level Prompts", 2)
        self.add_text("These prompts are used for initial system classification and are applied regardless of jurisdiction.")

        for file_name, file_info in organized_prompts["system_prompts"].items():
            file_display = file_name.replace("_", " ").title()
            self.add_header(f"{file_display}", 3)
            self.add_text(f"*File: `{file_info['file_path']}`*\n")

            sorted_prompts = sorted(file_info["prompts"].items())
            for prompt_name, prompt_content in sorted_prompts:
                self.add_prompt_section(prompt_name, prompt_content, 4)

        # Jurisdiction-specific prompts
        self.add_header("Jurisdiction-Specific Prompts", 2)
        self.add_text("These prompts are tailored for specific legal systems and jurisdictions.")

        # Generate sections for each jurisdiction
        for jurisdiction, jurisdiction_data in organized_prompts["jurisdiction_prompts"].items():
            if jurisdiction_data:  # Only include if there are prompts
                self.generate_jurisdiction_section(jurisdiction, jurisdiction_data)

        return "\n".join(self.content)


def main():
    """Main function to populate the README.md file."""
    script_dir = Path(__file__).parent
    prompts_dir = script_dir
    readme_path = prompts_dir / "README.md"

    print(f"Scanning for prompts in: {prompts_dir}")

    # Extract and organize all prompts
    extractor = PromptExtractor(str(prompts_dir))
    organized_prompts = extractor.organize_prompts()

    # Generate markdown documentation
    generator = MarkdownGenerator()
    markdown_content = generator.generate_markdown(organized_prompts)

    # Write to README.md
    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"Successfully wrote documentation to {readme_path}")

        # Print summary
        total_prompts = 0
        for category in organized_prompts.values():
            if isinstance(category, dict):
                for item in category.values():
                    if isinstance(item, dict) and "prompts" in item:
                        total_prompts += len(item["prompts"])
                    elif isinstance(item, dict):
                        for subitem in item.values():
                            if isinstance(subitem, dict) and "prompts" in subitem:
                                total_prompts += len(subitem["prompts"])

        print(f"Documented {total_prompts} prompts across multiple jurisdictions and categories.")

    except Exception as e:
        print(f"Error writing to {readme_path}: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
