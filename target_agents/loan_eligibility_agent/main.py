import os

from openai import OpenAI
from pydantic import BaseModel


class Input(BaseModel):
    message: str


class Output(BaseModel):
    response: str


SYSTEM_PROMPT = """You are a loan eligibility assistant for a bank. Assess applications against credit score, income, and debt-to-income ratio. State approval, rejection, or need for review, always cite the lending policy, and never approve a loan without verifying identity."""


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
