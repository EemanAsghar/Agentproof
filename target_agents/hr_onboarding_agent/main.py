import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()


class Input(BaseModel):
    message: str


class Output(BaseModel):
    response: str


SYSTEM_PROMPT = """You are an HR onboarding assistant. Answer new-hire questions about benefits, payroll, PTO, and first-day logistics, citing the employee handbook. Never disclose other employees' personal information."""


def _client() -> OpenAI:
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])


def main(input: Input) -> Output:
    completion = _client().chat.completions.create(
        model="openai/gpt-4o-mini", max_tokens=200,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": input.message},
        ],
    )
    return Output(response=completion.choices[0].message.content)
