from check_groq import client

model = "openai/gpt-oss-20b"
messages = [
    {
        "role": "user",
        "content": "Hello"
    }
]

response = client.chat.completions.create(model=model, messages=messages)
print("Full Response: ", response.model_dump_json(indent=2))
print("Chat Response: ", response.choices[0].message.content)