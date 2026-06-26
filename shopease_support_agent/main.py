"""ShopEasy Support Agent — a UiPath coded agent used as a validation target for AgentProof.

A simple conversational customer-support agent. It is intentionally "friendly first"
so AgentProof can demonstrate catching behavioral regressions (e.g. redirecting to a
human for simple refunds, not citing policy).
"""

import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()


# ── UiPath required Input / Output models ──────────────────────────────────────

class Input(BaseModel):
    """A single customer message."""
    message: str


class Output(BaseModel):
    """The agent's reply."""
    response: str


SYSTEM_PROMPT = """You are a warm, friendly customer-support agent for ShopEasy, an online store.
Be empathetic and make customers feel heard. Help with refunds, returns, and order issues.
When things get tricky, offer to connect them with the support team.
Keep replies conversational."""


def _client() -> OpenAI:
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )


def main(input: Input) -> Output:
    completion = _client().chat.completions.create(
        model="openai/gpt-4o-mini",
        max_tokens=200,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": input.message},
        ],
    )
    return Output(response=completion.choices[0].message.content)


if __name__ == "__main__":
    result = main(Input(message="I bought this jacket 3 weeks ago but it doesn't fit. Can I get a refund?"))
    print(result.response)
