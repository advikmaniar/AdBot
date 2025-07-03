from openai import OpenAI
import os
import re
from dotenv import load_dotenv
from constants import LLM_MODEL_3_5, SYSTEM_INTENT_CLASSIFIER_PROMPT, SYSTEM_SUBINTENT_CLASSIFIER_PROMPT, FINANCE_SUBINTENT_EXAMPLES

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def is_obvious_greeting(text: str) -> bool:
    return bool(re.match(r"^(hi|hello|hey|yo|sup|howdy|hola|hiya)[.!]*$", text.strip().lower()))

def is_obvious_all_set(text: str) -> bool:
    return bool(re.match(r"^(thank you|thanks|gracias|shukriya|im good|all set|end|cancel)[.!]*$", text.strip().lower()))

# Classify - Greeting, Finance, Other
def classify_intent(message: str) -> str:
    response = client.chat.completions.create(
        model=LLM_MODEL_3_5,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_INTENT_CLASSIFIER_PROMPT
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature=0,
        max_tokens=1
    )
    return response.choices[0].message.content.strip().lower()

# Subintents for finance - 'insights', 'statistics', or 'visualizations'.
def classify_finance_subintent(user_input: str) -> str:

    messages=[{"role": "system",
               "content": (SYSTEM_SUBINTENT_CLASSIFIER_PROMPT)},
        ]
    for label, phrases in FINANCE_SUBINTENT_EXAMPLES.items():
        for phrase in phrases:
            messages.append({"role": "user", "content": phrase})
            messages.append({"role": "assistant", "content": label})

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=LLM_MODEL_3_5,
        messages=messages,
        temperature=0,
        max_tokens=8
    )
    return response.choices[0].message.content.strip().lower()
