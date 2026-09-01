# ai/transliterate_schema.py
from pydantic import BaseModel, field_validator

TRANSLITERATE_SCHEMA = {
    "type": "object",
    "properties": {
        "best_guess_name": {"type": ["string", "null"]},
        "confidence": {"type": "number"},
    },
    "required": ["best_guess_name", "confidence"],
    "additionalProperties": False,
}


class TransliterateResult(BaseModel):
    best_guess_name: str | None
    confidence: float

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("confidence out of range")
        return v
