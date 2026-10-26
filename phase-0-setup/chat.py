from check_groq import client

model = "openai/gpt-oss-20b"
messages = [
    {
        "role": "system",
        "content": "You are a principal software engineer."  
    },
    {
        "role": "user",
        "content": "Explain how HTTP works in about 200 words."
    }
]

stream = client.chat.completions.create(model=model, messages=messages, stream=True, reasoning_effort="low",)

reply = ""
for chunk in stream:
    if not chunk.choices:
        continue
    
    text = chunk.choices[0].delta.content
    
    if text:
        print(text, end="", flush=True)
        reply += text
    
print()