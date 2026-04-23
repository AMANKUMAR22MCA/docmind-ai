from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb

# Load + chunk (you already know this!)
loader = PyPDFLoader(r"C:\Users\Aman.Kumar\Downloads\Resume (2).pdf")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# ChromaDB setup (you already know this too!)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("resume")

# YOUR TASK: fill these two blanks
texts = [chunk.page_content for chunk in chunks]   # 👈 extract .page_content from each chunk
ids   = [f"id{i}" for i in range(len(chunks))]  # 👈 generate "id0", "id1"... using f-string

collection.add(documents=texts, ids=ids)

print(f"✅ Stored {len(texts)} chunks!")  # 👈 how many?