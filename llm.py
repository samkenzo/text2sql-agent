import os
import time
from dotenv import load_dotenv
from groq import Groq, RateLimitError

load_dotenv()

# CHECK THIS: model names change and old ones get retired.
# Use the model from your prompt-lab, or pick one from console.groq.com/docs/models
DEFAULT_MODEL = "openai/gpt-oss-20b"
MODEL = os.getenv("T2S_MODEL", DEFAULT_MODEL)

client = Groq()  # reads GROQ_API_KEY from the environment (.env)


def ask_llm(system: str, user: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                temperature=0,  # 0 means the most deterministic output, which suits SQL
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}],
            )
            return resp.choices[0].message.content
        except RateLimitError:  # free tier has limits, so wait and retry
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("Rate limited too many times. Wait a minute and retry.")