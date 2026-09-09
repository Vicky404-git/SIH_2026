from ollama import chat

response = chat(
    model="qwen3-vl:4b",
    messages=[
        {
            "role": "user",
            "content": "Explain what Artificial Intelligence is in 3 simple sentences."
        }
    ]
)

print("\n===== QWEN RESPONSE =====\n")
print(response.message.content)