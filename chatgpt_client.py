import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a data extraction agent.

Convert messy field sales notes into STRICT JSON.
Return ONLY valid JSON.
No explanations.
No markdown.

Fields:
Date, Name, Phone, Location, Product,
Quantity, Price_per_Unit, Total, Feedback, Follow_Up

If a field is missing, return it as an empty string.
"""

def notes_to_json(notes: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": notes}
        ],
        temperature=0
    )

    raw = response.choices[0].message.content
    return json.loads(raw)
