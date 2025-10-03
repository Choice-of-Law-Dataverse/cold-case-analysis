import csv
import sys
from pathlib import Path


def test_batch_latam_analysis():
    """
    Batch analysis of LATAM case decision texts through the full pipeline.
    Outputs a CSV file with columns:
      filename, precise_jurisdiction, legal_system_type, col_section, theme, abstract,
      relevant_facts, pil_provisions, col_issue, courts_position
    """
    # Ensure streamlit and agent root on sys.path for imports
    STREAMLIT_DIR = Path(__file__).parent.parent
    if str(STREAMLIT_DIR) not in sys.path:
        sys.path.insert(0, str(STREAMLIT_DIR))
    AGENT_ROOT = STREAMLIT_DIR.parent  # cold_case_analyzer_agent
    if str(AGENT_ROOT) not in sys.path:
        sys.path.insert(0, str(AGENT_ROOT))

    # Import analysis steps
    from tools.case_analyzer import abstract, col_issue, courts_position, pil_provisions, relevant_facts
    from tools.col_extractor import extract_col_section
    from tools.jurisdiction_detector import detect_legal_system_type
    from tools.precise_jurisdiction_detector import detect_precise_jurisdiction
    from tools.themes_classifier import theme_classification_node

    # Locate LATAM text inputs
    txts_dir = AGENT_ROOT / "latam_case_analysis" / "txts"

    # Create txts directory if it doesn't exist
    txts_dir.mkdir(parents=True, exist_ok=True)

    txt_files = list(Path(txts_dir).glob("*.txt"))
    if not txt_files:
        # Create a sample test file if none exist
        sample_file = txts_dir / "sample_test_case.txt"
        sample_text = """
        SAMPLE COURT DECISION
        This is a sample court decision for testing purposes.
        The case involves choice of law issues in international contracts.
        The court considered applicable jurisdiction and international private law provisions.
        The decision addresses conflicts of law in cross-border commercial disputes.
        """
        sample_file.write_text(sample_text.strip(), encoding="utf-8")
        txt_files = [sample_file]
        print(f"Created sample test file at {sample_file}")

    assert txt_files, f"No text files found in {txts_dir}"

    # Prepare output CSV
    output_csv = STREAMLIT_DIR / "latam_analysis_results.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "filename", "precise_jurisdiction", "legal_system_type", "col_section", "theme", "abstract",
            "relevant_facts", "pil_provisions", "col_issue", "court's_position"
        ])

        # Process each text file
        for txt_path in txt_files:
            print(f"\nProcessing: {txt_path.name}")
            try:
                text = txt_path.read_text(encoding="utf-8")
                state = {"full_text": text}

                # 1. Precise jurisdiction detection
                try:
                    precise_jurisdiction = detect_precise_jurisdiction(text)
                    state["precise_jurisdiction"] = precise_jurisdiction
                    print(f"  - Precise jurisdiction: {precise_jurisdiction}")
                except Exception as e:
                    print(f"  - Error in jurisdiction detection: {e}")
                    precise_jurisdiction = "Unknown"
                    state["precise_jurisdiction"] = precise_jurisdiction

                # 2. Legal system type detection
                try:
                    legal_system_type = detect_legal_system_type(precise_jurisdiction, text)
                    state["jurisdiction"] = legal_system_type
                    print(f"  - Legal system type: {legal_system_type}")
                except Exception as e:
                    print(f"  - Error in legal system detection: {e}")
                    state["jurisdiction"] = "Unknown legal system"

                # 3. Choice of Law section extraction
                try:
                    res_col = extract_col_section(state)
                    state.update(res_col)
                    print("  - COL section extracted")
                except Exception as e:
                    print(f"  - Error in COL extraction: {e}")
                    state["col_section"] = ["Error in extraction"]

                # 4. Theme classification
                try:
                    res_theme = theme_classification_node(state)
                    state.update(res_theme)
                    print("  - Theme classified")
                except Exception as e:
                    print(f"  - Error in theme classification: {e}")
                    state["classification"] = ["Error in classification"]

                # 5. Relevant facts extraction
                try:
                    res_facts = relevant_facts(state)
                    state.update(res_facts)
                    print("  - Relevant facts extracted")
                except Exception as e:
                    print(f"  - Error in facts extraction: {e}")
                    state["relevant_facts"] = ["Error in extraction"]

                # 6. PIL provisions extraction
                try:
                    res_pil = pil_provisions(state)
                    state.update(res_pil)
                    print("  - PIL provisions extracted")
                except Exception as e:
                    print(f"  - Error in PIL provisions: {e}")
                    state["pil_provisions"] = [["Error in extraction"]]

                # 7. Choice of Law issue identification
                try:
                    res_issue = col_issue(state)
                    state.update(res_issue)
                    print("  - COL issue identified")
                except Exception as e:
                    print(f"  - Error in COL issue: {e}")
                    state["col_issue"] = ["Error in extraction"]

                # 8. Court's position summarization
                try:
                    res_pos = courts_position(state)
                    state.update(res_pos)
                    print("  - Court's position extracted")
                except Exception as e:
                    print(f"  - Error in court's position: {e}")
                    state["courts_position"] = ["Error in extraction"]

                # 9. Abstract extraction (moved to final step)
                try:
                    res_abs = abstract(state)
                    state.update(res_abs)
                    print("  - Abstract generated")
                except Exception as e:
                    print(f"  - Error in abstract generation: {e}")
                    state["abstract"] = ["Error in generation"]

                # Gather latest outputs with safe extraction
                def safe_get_last(data, default=""):
                    """Safely get the last item from a list or return default."""
                    if isinstance(data, list) and data:
                        return data[-1]
                    return data if data else default

                row = [
                    txt_path.name,
                    state.get("precise_jurisdiction", "Unknown"),
                    state.get("jurisdiction", "Unknown"),
                    safe_get_last(state.get("col_section", []), ""),
                    safe_get_last(state.get("classification", []), ""),
                    safe_get_last(state.get("abstract", []), ""),
                    safe_get_last(state.get("relevant_facts", []), ""),
                    safe_get_last(state.get("pil_provisions", []), []),
                    safe_get_last(state.get("col_issue", []), ""),
                    safe_get_last(state.get("courts_position", []), "")
                ]
                writer.writerow(row)
                print(f"  - Completed processing {txt_path.name}")

            except Exception as e:
                print(f"Error processing {txt_path.name}: {e}")
                # Write error row
                error_row = [txt_path.name, "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR"]
                writer.writerow(error_row)

    # Ensure CSV was written
    assert output_csv.exists(), f"Output CSV file was not created at {output_csv}"
    print(f"\nBatch analysis completed. Results saved to: {output_csv}")

if __name__ == "__main__":
    test_batch_latam_analysis()
    print("Batch LATAM analysis test completed successfully.")
