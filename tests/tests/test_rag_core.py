import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag_core import make_rag_prompt

def test_prompt_creation_english():
    """
    Tests if the prompt is correctly formatted for an English question.
    """
    question = "How do I fix the CRM?"
    passages = ["Solution: Reload the page.", "Cause: API timeout."]
    lang = "en"
    prompt = make_rag_prompt(question, passages, lang)

    # Assert that key components are in the final prompt
    assert "How do I fix the CRM?" in prompt
    assert "Reload the page" in prompt
    assert "API timeout" in prompt
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