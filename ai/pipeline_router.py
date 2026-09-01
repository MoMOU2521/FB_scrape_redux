# ai.pipeline_router.py
from ai.config import GATE1_MAX_CHARS, OVERSIZED_MAX_CHARS
from ai.extraction_pipeline import run_processing
from ai.gate1_pipeline import run_processing as run_gate1_processing
from ai.transliterate_pipeline import run_processing as run_transliterate_processing


class PipelineRouter:
    def __init__(self, gate1_ai, extraction_ai, transliterate_ai=None):
        self.gate1_ai = gate1_ai
        self.extraction_ai = extraction_ai
        self.transliterate_ai = transliterate_ai

    def should_run_gate1(self, post):
        return len(post["text"]) <= GATE1_MAX_CHARS

    def process_gate1(self, post):
        return run_gate1_processing(self.gate1_ai, post)

    def process_extraction(self, post):
        return run_processing(self.extraction_ai, post)

    def process_transliterate(self, building_input: dict):
        return run_transliterate_processing(self.transliterate_ai, building_input)
