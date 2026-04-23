# import chromadb

# # Step 1: Create a ChromaDB "database" in memory
# client = chromadb.Client()

# # Step 2: Create a "collection" (like a table in PostgreSQL)
# collection = client.create_collection("my_first_collection")

# # Step 3: Store 3 sentences
# collection.add(
#     documents=[
#         "Python is a programming language",
#         "Dogs are loyal animals",
#         "FastAPI is great for building APIs"
#     ],
#     ids=["id1", "id2", "id3"]   # every item needs a unique ID

# )

# results = collection.query(
#     query_texts= ["programming"],
#     n_results=3  
# )
# print(results["documents"])
# print("✅ Stored 3 documents in ChromaDB!")
# print(f"Total items: {collection.count()}")


# import chromadb

# # Change this one line to save to disk
# client = chromadb.PersistentClient(path="./chroma_db")  # 👈 use "./chroma_db"

# collection = client.get_or_create_collection("my_first_collection")

# collection.add(
#     documents=[
#         "Python is a programming language",
#         "Dogs are loyal animals",
#         "FastAPI is great for building APIs"
#     ],
#     ids=["id1", "id2", "id3"]
# )

# results = collection.query(
#     query_texts=["animals"],
#     n_results=2
# )

# print(results["documents"])


import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("documents")

print(f"Total chunks in DB: {collection.count()}")

# Print ALL chunks
results = collection.get()
for i, doc in enumerate(results["documents"]):
    print(f"\n--- Chunk {i} ---")
    print(doc[:100])  # first 100 chars of each chunk