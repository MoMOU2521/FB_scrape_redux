# ai.extraction_pipeline.py
from ai.prompts.extraction import PROCESSING_SYSTEM_PROMPT
from ai.helpers import strip_markdown_links
from ai.listing_schema import LISTING_SCHEMA


def run_processing(ai, post):
    cleaned_text = strip_markdown_links(post["text"])
    return ai.complete(
        system_prompt=PROCESSING_SYSTEM_PROMPT,
        user_prompt=cleaned_text,
        schema=LISTING_SCHEMA,
        schema_name="listing_extraction",
    )
