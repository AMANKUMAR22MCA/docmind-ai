# from groq import Groq
# from dotenv import load_dotenv
# import os

# load_dotenv()

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# response = client.chat.completions.create(
#     model="llama-3.1-8b-instant",
#     messages=[
#         {"role": "user", "content": "What is FastAPI in one line?"}
#     ]
# )

# print(response.choices[0].message.content)



import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the model
model = genai.GenerativeModel("gemini-2.5-flash")  # or "gemini-1.5-pro" for more powerful

# Generate response
response = model.generate_content("What is FastAPI in one line?")

print(response.text)


from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  # free, runs locally
embedding = model.encode("FastAPI is a web framework")
print(len(embedding))  # should print 384 numbers
print(embedding[:5])   # first 5 numbers