# from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
load_dotenv()

# Block 1: LLM
llm = ChatGoogleGenerativeAI(
    # model="llama-3.1-8b-instant",
    model="gemini-2.5-flash",       # 👈 same model you've been using
    temperature=0   ,
    google_api_key=os.getenv("GEMINI_API_KEY")       # 0 = consistent answers
)

# Block 2: Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that explains tech concepts simply."),
    ("user", "{question}")   # 👈 variable name — call it "question"
])

# Block 3: Chain (connecting prompt + llm)
chain = prompt | llm   # 👈 prompt | llm  (pipe operator!)

# Run it
response = chain.invoke({"question": "What is LangChain in 2 lines?"})
print(response.content)   # 👈 hint: same as before — .content