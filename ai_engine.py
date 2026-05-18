import json
from openai import OpenAI
from prompts import SYSTEM_PROMPT

client = OpenAI()



def generate_ai_response(customer_requirement):

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": customer_requirement
            }
        ],
        temperature=0.7
    )

    ai_text = response.choices[0].message.content

    try:
        cleaned_text = ai_text.replace("```json", "").replace("```", "")
        return json.loads(cleaned_text)

    except Exception as e:
        raise Exception(f"AI Response Parsing Failed: {str(e)}")