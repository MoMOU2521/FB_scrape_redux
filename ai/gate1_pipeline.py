# ai.gate1_pipeline.py
from ai.prompts.gate1 import GATE1_SYSTEM_PROMPT
from ai.helpers import strip_markdown_links


def run_processing(ai, post):
    cleaned_text = strip_markdown_links(post["text"])
    return ai.complete(
        system_prompt=GATE1_SYSTEM_PROMPT,
        user_prompt=cleaned_text,
    )
