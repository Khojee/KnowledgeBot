from src.rag_core import make_rag_prompt

def test_prompt_creation_english():
    """
    Tests if the prompt is correctly formatted for an English question.
    """
    question = "How do I fix the CRM?"
    passages = ["Solution: Reload the page.", "Cause: API timeout."]
    lang = "en"
    prompt = make_rag_prompt(question, passages, lang)

    assert "How do I fix the CRM?" in prompt
    assert "Reload the page" in prompt
    assert "write your entire response in English" in prompt

def test_prompt_creation_russian():
    """
    Tests if the prompt correctly changes the language instruction for Russian.
    """
    question = "Как починить CRM?"
    passages = ["Solution: Reload the page."]
    lang = "ru"
    prompt = make_rag_prompt(question, passages, lang)
    
    assert "Как починить CRM?" in prompt
    assert "write your entire response in Russian" in prompt