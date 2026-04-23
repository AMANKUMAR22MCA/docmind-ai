from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
loader = PyPDFLoader(r"C:\Users\Aman.Kumar\Downloads\Resume (2).pdf")  # 👈 any PDF path on your computer

docs = loader.load()

print(f"Total pages: {len(docs)}")   # 👈 len of docs
print(f"First page text: {docs[0].page_content[:200]}")  # first 200 chars


splitter = RecursiveCharacterTextSplitter(
    chunk_size= 200,       # 👈 each chunk = 200 characters
    chunk_overlap= 50     # 👈 overlap between chunks = 50 characters
)

chunks = splitter.split_documents(docs)

print(f"Total chunks: {len(chunks)}")
print(f"First chunk:\n{chunks[0].page_content}")