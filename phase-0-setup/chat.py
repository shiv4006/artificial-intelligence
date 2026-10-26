import argparse
from check_groq import client

parser = argparse.ArgumentParser(description="Terminal Chatbot")

# model = "openai/gpt-oss-20b"

parser.add_argument("--system", default="You are a helpful assistant. Answer in txt format.")
parser.add_argument("--model", default="openai/gpt-oss-20b")
parser.add_argument("--reasoning_effort", default="low")
args = parser.parse_args()

messages = [
    { "role": "system", "content": args.system }
]

# Calling Function
def chatbot():
    stream = client.chat.completions.create(
        model=args.model,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
        reasoning_effort=args.reasoning_effort,
    )

    reply = ""
    usage = None
    for chunk in stream:
        if chunk.usage:
            usage = chunk.usage
            
        if not chunk.choices:
            continue
        
        # print("Chunk: ", chunk)
        text = chunk.choices[0].delta.content
        
        if text:
            print(text, end="", flush=True)
            reply += text
        
    if usage:
        print()
        print("Prompt Tokens: ", usage.prompt_tokens)
        print("Completion Tokens: ", usage.completion_tokens)
            
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
    