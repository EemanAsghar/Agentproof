from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Aria — Demo Customer Support Agent")


def _get_client() -> OpenAI:
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )

# BASELINE — passes all behavioral contracts
PROMPT_V1 = """
You are a customer support agent for ShopEasy, an e-commerce company.

Rules you must always follow:
1. For purchases within 30 days, always confirm the customer is eligible for a refund.
2. Always cite the relevant policy: reference ShopEasy Return Policy Section 3.1.
3. Keep responses under 100 words.
4. Never tell customers to contact the support team for simple refund requests.
5. Always be professional and helpful.
"""

# REGRESSED — after friendly prompt tweak, breaks 3 contracts
PROMPT_V2 = """
You are a super friendly and warm customer support agent for ShopEasy!
Be casual, empathetic, and make customers feel heard.
When things get complicated, always offer to connect them with our amazing support team.
Keep it conversational and do not worry too much about policies.
"""


class ChatRequest(BaseModel):
    message: str


@app.post("/v1/chat")
async def chat_v1(request: ChatRequest):
    """Baseline Aria — passes all contracts."""
    response = _get_client().chat.completions.create(
        model="openai/gpt-4o-mini",
        max_tokens=200,
        messages=[
            {"role": "system", "content": PROMPT_V1},
            {"role": "user", "content": request.message},
        ],
    )
    return {"response": response.choices[0].message.content}


@app.post("/v2/chat")
async def chat_v2(request: ChatRequest):
    """Regressed Aria — fails 3 behavioral contracts."""
    response = _get_client().chat.completions.create(
        model="openai/gpt-4o-mini",
        max_tokens=200,
        messages=[
            {"role": "system", "content": PROMPT_V2},
            {"role": "user", "content": request.message},
        ],
    )
    return {"response": response.choices[0].message.content}


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "Aria", "version": "demo"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("demo_agent.main:app", host="0.0.0.0", port=8000, reload=True)
