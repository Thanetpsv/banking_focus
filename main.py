from fastapi import FastAPI, Request
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

app = FastAPI()

class Ingredients(BaseModel):
    items: list[str]

@app.post("/suggest")
async def suggest(ingredients: Ingredients):
    prompt = f"""You are a helpful cooking assistant.
The user has the following ingredients: {', '.join(ingredients.items)}.
They also have access to basic seasonings (salt, pepper, oil, etc.) and basic cookware (microwave, stove, oven, blender).
Suggest 3 meal ideas they can make, and briefly describe each (1-2 sentences)."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )
    return {"suggestions": response.choices[0].message.content}
