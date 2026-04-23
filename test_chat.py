from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

messages = [
        {"role": "system", "content": """You are a Professional Resume Reviewer with 10 years of experience in HR and tech hiring.

Rules:
1. Never rewrite entire sections — instead, highlight weak phrases and suggest 2-3 specific improvements
2. Always identify at least one strength before giving criticism

Tone: Constructive and specific, like a senior colleague doing a peer review. Use bullet points for clarity."""}
]

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    # add quit condition here ← you write this
    
    messages.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )
    
    reply = response.choices[0].message.content
    print(f"AI: {reply}")
    print("--------------------------------")
    messages.append({"role":"assistant","content":reply})
    
    # add reply to history ← you write this