import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "llama-3.3-70b-versatile"


def generate_text(prompt: str, max_new_tokens: int = 1000):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert Research Intelligence Assistant. "
                        "Generate detailed, academic, well-structured responses. "
                        "Complete every answer and never stop in the middle."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_completion_tokens=max_new_tokens,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Groq Error: {e}"


if __name__ == "__main__":
    print(generate_text("What is Artificial Intelligence?"))