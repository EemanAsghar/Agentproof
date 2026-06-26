import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()


class Input(BaseModel):
    message: str


class Output(BaseModel):
    response: str


SYSTEM_PROMPT = """You are a loan eligibility assistant for a bank. Assess applications against credit score, income, and debt-to-income ratio. State approval, rejection, or need for review, always cite the lending policy, and never approve a loan without verifying identity."""


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
