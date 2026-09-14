# ai/config.py

GATE1_PROMPT_VERSION = "v1"
EXTRACTION_PROMPT_VERSION = "v1"
TRANSLITERATE_PROMPT_VERSION = "v1"

GATE1_MODEL = "openai/gpt-oss-20b"
EXTRACTION_MODEL = "openai/gpt-oss-120b"
# EXTRACTION_MODEL = "qwen/qwen3.6-27b"
# TRANSLITERATE_MODEL = "openai/gpt-oss-120b"
TRANSLITERATE_MODEL = "qwen/qwen3.8-27b"

GATE1_MAX_CHARS = 2000
OVERSIZED_MAX_CHARS = 2500

# ------------------------------------------------------------
# Model Control Panel — generation dials only.
# response_format here is a DEFAULT/FALLBACK, used only when a
# pipeline call doesn't pass its own schema. Schema itself is a
# task concern, supplied per-call via complete(schema=..., schema_name=...).
# ------------------------------------------------------------
MODEL_CONTROLS = {
    "openai/gpt-oss-120b": {
        "temperature": 0.0,
        "top_p": 1.0,
        "max_completion_tokens": 1200,
        "reasoning_effort": "low",
        "reasoning_format": "parsed",
        "response_format": {"type": "json_object"},
        "stop": None,
        "stream": False,
        "seed": None,
    },
    "qwen/qwen3.8-27b": {
        "temperature": 0.0,
        "top_p": 1.0,
        "max_completion_tokens": 1200,
        "reasoning_effort": "none",
        "reasoning_format": "parsed",
        "supports_json_schema": False,
        "response_format": {"type": "json_object"},
        "stream": False,
    },
    "openai/gpt-oss-20b": {
        "temperature": 0.0,
        "top_p": 1.0,
        "max_completion_tokens": 1200,
        "reasoning_effort": "low",
        "reasoning_format": "parsed",
        "response_format": {"type": "json_object"},
        "stop": None,
        "stream": False,
        "seed": None,
    },
}
