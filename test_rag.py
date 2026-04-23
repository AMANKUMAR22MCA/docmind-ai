from groq import Groq
import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("resume")

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

question = "For Aman which company he worked as Implementation Engineer?"

# Step 1: Search ChromaDB
results = collection.query(
    query_texts=[question],   # 👈 the question
    n_results=3        # 👈 top 3 chunks
)

# Step 2: Join chunks into one context string
context = "\n".join(results["documents"][0])   # 👈 which key?

# Step 3: Send to Groq
response = groq_client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "Answer using only the context provided."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
    ]
)

print(response.choices[0].message.content)