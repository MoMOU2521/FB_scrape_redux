# ai/groq_ai_client.py

import time
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from groq import APIStatusError

from .config import MODEL_CONTROLS

load_dotenv()


class GroqAIClient:
    def __init__(self, model, rpm=30):
        self.client = Groq()
        self.model = model
        self.max_retries = 3
        self.retry_delay = 60
        self.max_requests_per_day = None
        self.request_count_today = 0
        self.today_date = datetime.now().date()
        self.rpm = rpm
        self.min_interval = 10.0 / rpm
        self.last_request_time = 0

        self.controls = MODEL_CONTROLS.get(model)
        if self.controls is None:
            raise ValueError(f"No control configuration found for model: {model}")

    def set_daily_limit(self, limit):
        self.max_requests_per_day = limit
        print(f"Daily limit set to {limit} requests")

    def _reset_if_new_day(self):
        today = datetime.now().date()
        if today != self.today_date:
            self.request_count_today = 0
            self.today_date = today

    def _check_limits(self):
        self._reset_if_new_day()
        if self.max_requests_per_day is None:
            return
        if self.request_count_today >= self.max_requests_per_day:
            raise Exception(f"DAILY_LIMIT_REACHED: {self.max_requests_per_day}")

    def _wait_if_needed(self):
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def complete(
        self,
        system_prompt,
        user_prompt,
        temperature=None,
        reasoning_effort=None,
        schema=None,
        schema_name=None,
    ):
        """
        Optional override params: if provided, they temporarily override the config values.
        This allows per-call tuning without editing the config file.

        schema/schema_name: if provided, builds a strict json_schema response_format
        for this call only, regardless of what's in model config. This is a TASK
        concern, not a model concern — the caller (pipeline) decides if/what schema
        it needs, the model config only supplies generation dials.
        """
        self._check_limits()
        self._wait_if_needed()

        effective_temperature = (
            temperature if temperature is not None else self.controls["temperature"]
        )
        effective_reasoning_effort = (
            reasoning_effort
            if reasoning_effort is not None
            else self.controls.get("reasoning_effort")
        )

        if schema is not None and self.controls.get("supports_json_schema", False):
            effective_response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name or "response",
                    "strict": True,
                    "schema": schema,
                },
            }
        else:
            effective_response_format = self.controls.get("response_format")

        for attempt in range(self.max_retries):
            try:
                response = self._call(
                    system_prompt,
                    user_prompt,
                    temperature=effective_temperature,
                    reasoning_effort=effective_reasoning_effort,
                    response_format=effective_response_format,
                )

                if response["finish_reason"] == "length":
                    print("Truncated — retrying with reasoning_effort='none' or 'low'")
                    fallback_effort = "none" if "qwen" in self.model else "low"
                    response = self._call(
                        system_prompt,
                        user_prompt,
                        temperature=effective_temperature,
                        reasoning_effort=fallback_effort,
                        response_format=effective_response_format,
                    )

                self.request_count_today += 1
                return response

            except APIStatusError as e:
                if e.status_code == 429:
                    print(
                        f"Rate limit hit. Waiting {self.retry_delay}s... (attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(self.retry_delay)
                    continue
                elif e.status_code == 400:
                    print(
                        f"Schema validation failed on attempt {attempt + 1}/{self.max_retries}: {e}"
                    )
                    continue
                else:
                    raise

        raise Exception(f"Failed after {self.max_retries} attempts")

    def _call(
        self, system_prompt, user_prompt, temperature, reasoning_effort, response_format
    ):
        """Constructs the API call. response_format is passed in by complete(),
        already resolved (either call-time schema or model-config default)."""

        kwargs = {
            "model": self.model,
            "temperature": temperature,
            "top_p": self.controls.get("top_p", 1.0),
            "max_completion_tokens": self.controls.get("max_completion_tokens"),
            "response_format": response_format,
            "stop": self.controls.get("stop"),
            "stream": self.controls.get("stream", False),
            "seed": self.controls.get("seed"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        if "reasoning_effort" in self.controls:
            kwargs["reasoning_effort"] = reasoning_effort
        if "reasoning_format" in self.controls:
            kwargs["reasoning_format"] = self.controls["reasoning_format"]

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resp = self.client.chat.completions.create(**kwargs)

        message = resp.choices[0].message
        return {
            "content": message.content,
            "reasoning": getattr(message, "reasoning", None),
            "finish_reason": resp.choices[0].finish_reason,
        }
