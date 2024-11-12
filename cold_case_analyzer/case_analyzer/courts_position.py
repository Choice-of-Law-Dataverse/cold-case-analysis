from llm_handler.model_access import prompt_model

def extract_courts_position(text, prompt, model):
    prompt_position = f"""{prompt}
    
                Here is the text of the Court Decision:
                {text}
                """
    return prompt_model(prompt_position, model)
