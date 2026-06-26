import os

from openai import OpenAI
from pydantic import BaseModel


class Input(BaseModel):
    message: str


class Output(BaseModel):
    response: str


SYSTEM_PROMPT = """You are an IT helpdesk triage agent. Categorize tickets by urgency, suggest first-line troubleshooting steps, and escalate hardware failures and security incidents immediately. Keep replies clear and actionable."""


def _api_key() -> str:
    try:
        from uipath.platform import UiPath
        sdk = UiPath()
        try:
            k = sdk.assets.retrieve_secret("OPENROUTER_API_KEY", folder_path="Shared")
            if k:
                return k
        except Exception:
            pass
        try:
            a = sdk.assets.retrieve("OPENROUTER_API_KEY", folder_path="Shared")
            v = getattr(a, "value", None) or getattr(a, "string_value", None) or getattr(a, "StringValue", None)
            if v:
                return v
        except Exception:
            pass
    except Exception:
        pass
    return os.environ["OPENROUTER_API_KEY"]


def main(input: Input) -> Output:
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=_api_key())
    completion = client.chat.completions.create(
        model="openai/gpt-4o-mini", max_tokens=200,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": input.message},
        ],
    )
    return Output(response=completion.choices[0].message.content)
