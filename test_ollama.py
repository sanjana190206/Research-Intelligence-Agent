import ollama

print("Starting...")

try:
    response = ollama.chat(
        model="llama3.2:latest",
        messages=[
            {
                "role": "user",
                "content": "What is Artificial Intelligence?"
            }
        ],
        options={
            "num_predict": 100,
            "temperature": 0.2,
        }
    )

    print("Response received!")
    print(response["message"]["content"])

except Exception as e:
    print("Error:", e)