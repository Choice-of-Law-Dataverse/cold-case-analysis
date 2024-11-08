from llm_handler.model_access import prompt_llama

def extract_rules_of_law(text, prompt):
    prompt_rules = f"""Here is the text of a Court Decision:
                {text}
                {prompt}
                """
    return prompt_llama(prompt_rules)
