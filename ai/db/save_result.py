# db.services.ai_processing.save_gate1_result.py
from __future__ import annotations

from db.database import db


def save_gate1_result(
    row_id: int,
    result_json: str,
    reasoning: str,
    prompt_version: str,
) -> None:
    db.conn.execute(
        """
        UPDATE posts
        SET result_json_v1 = ?,
            gate1_reasoning = ?,
            gate1_prompt_version = ?
        WHERE id = ?
        """,
        (result_json, reasoning, prompt_version, row_id),
    )
    db.conn.commit()


def save_extraction_result(
    row_id: int,
    result_json: str,
    reasoning: str,
    prompt_version: str,
) -> None:
    db.conn.execute(
        """
        UPDATE posts
        SET extraction_result_json = ?,
            extraction_reasoning = ?,
            extraction_prompt_version = ?
        WHERE id = ?
        """,
        (result_json, reasoning, prompt_version, row_id),
    )
    db.conn.commit()
