# to run the app locally, run the following on terminal: 
# 1) Activate venv: source venv/bin/activate 
# 2) run: uvicorn main:app --reload
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
    allow_extra: bool = False
    detail_for: str = None

@app.post("/suggest")
async def suggest(ingredients: Ingredients):
    if ingredients.detail_for:
        # Detailed recipe request
        prompt = f"""You are a helpful cooking assistant.
The user wants to cook: {ingredients.detail_for}
They have the following ingredients: {', '.join(ingredients.items)}.
They also have access to basic seasonings (salt, pepper, oil, soy sauce, oyster sauce) and basic cookware (microwave, stove, oven, blender).
Suggest a credible, step-by-step recipe for this dish, drawing from trusted cookbooks and culinary websites. List all ingredients needed (including amounts), then provide clear, numbered instructions for how to make the dish. If the user's ingredients are insufficient, you may suggest minor extras if allow_extra is True, but only if they are commonly available and truly improve the dish. Do not invent obscure or controversial ingredients or steps. Format your response as:
Ingredients:
- ingredient 1: amount
- ingredient 2: amount
Instructions:
1. Step one
2. Step two
..."""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        # Parse response into ingredients, measures, instructions
        content = response.choices[0].message.content
        # Simple parsing
        ingredients_list = []
        measures_list = []
        instructions_list = []
        in_ingredients = False
        in_instructions = False
        import re
        step_pattern = re.compile(r"^(\d+)\.\s*(.*)")
        for line in content.splitlines():
            line = line.strip()
            if line.lower().startswith("ingredients:"):
                in_ingredients = True
                in_instructions = False
                continue
            if line.lower().startswith("instructions:"):
                in_ingredients = False
                in_instructions = True
                continue
            if in_ingredients and line.startswith("-"):
                # Format: - ingredient: amount
                parts = line[1:].split(":", 1)
                if len(parts) == 2:
                    ingredients_list.append(parts[0].strip())
                    measures_list.append(parts[1].strip())
                else:
                    ingredients_list.append(parts[0].strip())
                    measures_list.append("")
            if in_instructions:
                match = step_pattern.match(line)
                if match:
                    instructions_list.append(match.group(2).strip())
        return {
            "ingredients": ingredients_list,
            "measures": measures_list,
            "instructions": instructions_list
        }
    else:
        if ingredients.allow_extra:
            prompt = f"""You are a helpful cooking assistant.
The user has the following ingredients: {', '.join(ingredients.items)}.
They also have access to basic seasonings (salt, pepper, oil, soy sauce, oyster sauce) and basic cookware (microwave, stove, oven, blender).
If you think the dish would benefit from a minor extra ingredient, you may suggest adding it, but only if it would truly improve the dish and is commonly available. If the provided ingredients do not go well together, leave them out of the recipe. Also leave out any ingredients deemed controversial, offensive, or not suitable for a general audience.
Suggest 3 meal ideas they can make, and briefly describe each (1-2 sentences). Draw inspiration from credible sources like cookbooks, culinary websites, do not invent unusual or obscure dishes and combinations of ingredients."""
        else:
            prompt = f"""You are a helpful cooking assistant.
The user has the following ingredients: {', '.join(ingredients.items)}.
They also have access to basic seasonings (salt, pepper, oil, soy sauce, oyster sauce) and basic cookware (microwave, stove, oven, blender).
Do NOT suggest any ingredients beyond those provided and the basic seasonings/cookware. If the provided ingredients do not go well together, leave them out of the recipe. Also leave out any ingredients deemed controversial, offensive, or not suitable for a general audience.
Suggest 3 meal ideas they can make, and briefly describe each (1-2 sentences). Draw inspiration from credible sources like cookbooks, culinary websites, do not invent unusual or obscure dishes and combinations of ingredients."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return {"suggestions": response.choices[0].message.content}
