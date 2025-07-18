from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def suggest_recipes(ingredients):
    prompt = f"""You are a helpful cooking assistant.
The user has the following ingredients: {', '.join(ingredients)}.
They also have access to basic seasonings (salt, pepper, oil, etc.) and basic cookware (microwave, stove, oven, blender).
Suggest 3 meal ideas they can make, and briefly describe each (1-2 sentences)."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4o" if needed
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content

def main():
    ingredients_input = input("Enter the ingredients you have, separated by commas: ")
    ingredients = [item.strip() for item in ingredients_input.split(",")]
    suggestions = suggest_recipes(ingredients)
    print("\nHere are 3 dish ideas you can make:\n")
    print(suggestions)

if _name_ == "_main_":
    main()