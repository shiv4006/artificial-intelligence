from check_groq import client

model = "openai/gpt-oss-20b"
messages = [
    {
        "role": "system",
        "content": "Answer user question under 200 words only."  
    }
]

# Calling Function
def chatbot():
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
    assistant_message = {
        "role": "assistant",
        "content": reply
    }
    
    messages.append(assistant_message)
    
# Entry Point
while(True):
    user_input = input("Ask you question or -1 to exit: ")
    
    if (user_input == "-1"):
        break
    else:
        user_message = {
            "role": "user",
            "content": user_input
        }

        messages.append(user_message)
        chatbot()
    