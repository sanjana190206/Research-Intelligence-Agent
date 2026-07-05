from dotenv import load_dotenv
import os

load_dotenv()

print("API KEY:", os.getenv("IBM_API_KEY"))
print("PROJECT ID:", os.getenv("PROJECT_ID"))
print("URL:", os.getenv("IBM_URL"))
from rag.granite_client import generate_text

if __name__ == "__main__":
    response = generate_text(
        prompt="What is Artificial Intelligence?",
        max_new_tokens=100
    )
    print(response)
