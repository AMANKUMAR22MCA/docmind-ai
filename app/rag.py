# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from groq import Groq
# import chromadb
# import os
# from dotenv import load_dotenv
# import datetime
# from langchain_google_genai import ChatGoogleGenerativeAI


# load_dotenv()

# # ChromaDB setup (you already know this!)
# client = chromadb.PersistentClient(path="./chroma_db")         # 👈 same path as before
# collection = client.get_or_create_collection("documents")    # 👈 call it "documents"

# # Groq setup (you did this in test_groq.py!)
# llm_client = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",       
#     temperature=0,
#     google_api_key=os.getenv("GEMINI_API_KEY"))


# def ingest_pdf(pdf_path: str, pdf_id: str):
#     # Step 1: Load PDF (you know this!)
#     loader = PyPDFLoader(pdf_path)
#     docs = loader.load()

#     # Step 2: Chunk it (you know this!)
#     splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#     chunks = splitter.split_documents(docs)

#     # Step 3: Prepare for ChromaDB (you wrote this exact code in test_store.py!)
#     texts = [chunk.page_content for chunk in chunks]
#     ids   = [f"{pdf_id}_chunk{i}" for i in range(len(chunks))]

#     # Step 4: Store in ChromaDB
#     collection.add(documents=texts, ids=ids)

#     return f"✅ Stored {len(texts)} chunks from {pdf_id}"

# def ask_question(question: str, pdf_id: str):
#     results = collection.query(
#         query_texts=[question],
#         n_results=7,
#     )
#     context = "\n".join(results["documents"][0])
    
#     today = datetime.date.today().strftime("%B %d, %Y")
    
#     response = llm_client.invoke([
#         {"role": "system", "content": f"""Today's date is {today}.
# Answer ONLY using the context provided.
# List ONLY direct employers — ignore client/partner company names in job descriptions.
# Do NOT include universities, colleges or educational institutions as employers.
# If the answer is not in the context, say 'I don't have enough information'.
# """},
#         {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
#     ])
    
#     return response.content   # 👈 Gemini uses .content same as before



import datetime
import json
import os
import re
import typing
import redis
import chromadb
from dotenv import load_dotenv
from groq import Groq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

_NA = "na"
_EMAIL_RE = re.compile(
    r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9._%+-])"
)
_PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s().-]*)?(?:\(?\d{2,4}\)?[\s().-]*)?\d{3,4}[\s().-]*\d{3,6}"
)
_HEADER_SKIP_RE = re.compile(
    r"(?i)^(resume|curriculum vitae|cv|summary|objective|profile|education|experience|skills|contact)$"
)

# ChromaDB setup
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("documents")
redis_client = redis.Redis(host="localhost", port=6379, db=2, decode_responses=True)


class DocumentQueryError(Exception):
    """Chroma/vector lookup failed; API should return 503 with a clear JSON error."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


# Groq setup
llm_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _digits_only(value: str) -> str:
    return re.sub(r"\D", "", value)


def _extract_first_json_object(text: str) -> typing.Optional[dict]:
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for idx, ch in enumerate(text[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                snippet = text[start : idx + 1]
                try:
                    parsed = json.loads(snippet)
                except json.JSONDecodeError:
                    return None
                if isinstance(parsed, dict):
                    return parsed
                return None
    return None


def _extract_name_heuristic(full_text: str) -> str:
    for line in full_text.splitlines()[:25]:
        candidate = line.strip()
        if not candidate or len(candidate) > 80:
            continue
        if _HEADER_SKIP_RE.match(candidate):
            continue
        if "@" in candidate or _PHONE_RE.search(candidate):
            continue
        if candidate.lower().startswith(("http://", "https://", "www.")):
            continue
        name_label = re.match(r"(?i)^name\s*:\s*(.+)$", candidate)
        if name_label and name_label.group(1).strip():
            return name_label.group(1).strip()
        if re.match(r"^[A-Za-z][A-Za-z\s.'`-]{1,78}[A-Za-z]$", candidate):
            words = candidate.split()
            if 1 <= len(words) <= 5:
                return candidate
    return _NA


def extract_resume_contact_json(full_text: str) -> dict[str, str]:
    contact = {"name": _NA, "phone": _NA, "email": _NA}
    if not full_text or not full_text.strip():
        return contact

    email_match = _EMAIL_RE.search(full_text)
    if email_match:
        contact["email"] = email_match.group(0).strip()

    phones = [_digits_only(match.group(0)) for match in _PHONE_RE.finditer(full_text)]
    valid_phones = [phone for phone in phones if len(phone) >= 10]
    if valid_phones:
        contact["phone"] = max(valid_phones, key=len)

    contact["name"] = _extract_name_heuristic(full_text)

    if _NA in contact.values():
        response = llm_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract contact information from resume text. Return ONLY valid JSON with keys "
                        'name, phone, email. Use "na" for missing values. Do not add extra keys.'
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Existing extraction: {json.dumps(contact)}\n\n"
                        f"Resume text:\n{full_text[:10000]}"
                    ),
                },
            ],
        )
        content = response.choices[0].message.content or ""
        parsed = _extract_first_json_object(content)
        if parsed:
            for key in ("name", "phone", "email"):
                value = parsed.get(key)
                if isinstance(value, str) and value.strip() and contact[key] == _NA:
                    cleaned = value.strip()
                    if key == "phone" and cleaned.lower() != _NA:
                        cleaned = _digits_only(cleaned) or _NA
                    contact[key] = cleaned

    return contact


def ingest_pdf(pdf_path: str, pdf_id: str):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    full_text = "\n".join(doc.page_content or "" for doc in docs)
    contact = extract_resume_contact_json(full_text)

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    texts = [chunk.page_content for chunk in chunks]
    ids = [f"{pdf_id}_chunk{i}" for i in range(len(chunks))]
    base_metadata = {
        "pdf_id": pdf_id,
        "name": contact["name"],
        "phone": contact["phone"],
        "email": contact["email"],
    }
    metadatas = [dict(base_metadata) for _ in texts]

    collection.add(documents=texts, ids=ids, metadatas=metadatas)
    return f"✅ Stored {len(texts)} chunks from {pdf_id}"


def _retrieve_chunks_for_question(pdf_id: str, question: str) -> tuple[list[str], list[dict]]:
    """
    Prefer semantic query filtered by pdf_id; on Chroma internal errors, fall back to
    unranked chunks from collection.get (same filter) so /ask still returns 200 when possible.
    """
    try:
        got = collection.get(
            where={"pdf_id": pdf_id},
            limit=120,
            include=["documents", "metadatas"],
        )
    except Exception as exc:
        raise DocumentQueryError(
            f"Vector store read failed for this document. Try Clear Cache, re-upload the PDF, "
            f"or restart after a Chroma issue. ({exc})"
        ) from exc

    all_docs = [d for d in (got.get("documents") or []) if isinstance(d, str) and d.strip()]
    all_metas = list(got.get("metadatas") or [])
    if not all_docs:
        return [], []

    try:
        results = collection.query(
            query_texts=[question],
            n_results=min(7, max(1, len(all_docs))),
            where={"pdf_id": pdf_id},
        )
        qdocs = (results.get("documents") or [[]])[0] or []
        qmetas = (results.get("metadatas") or [[]])[0] or []
        if qdocs:
            return qdocs, qmetas
    except Exception as exc:
        print(f"Chroma query failed (using unranked chunks): {exc!r}")

    cap = min(7, len(all_docs))
    return all_docs[:cap], all_metas[:cap]


def ask_question(
    question: str,
    pdf_id: str,
    history: list | None = None,
    cache_mode: str = "context",
):
    safe_history = history if isinstance(history, list) else []
    normalized_question = question.strip().lower()
    if cache_mode == "question_only":
        cache_key = f"{pdf_id}_{normalized_question}_question_only"
    else:
        history_hash = json.dumps(safe_history, ensure_ascii=True, sort_keys=True)
        cache_key = f"{pdf_id}_{normalized_question}_{history_hash}_context"
    cached_result = redis_client.get(cache_key)
    if cached_result:
        print("✅ Cache hit!")
        return cached_result

    docs, metadatas = _retrieve_chunks_for_question(pdf_id, question)
    if not docs:
        return (
            "I don't have enough information. "
            "No indexed text was found for this PDF id yet — wait for upload processing to finish, "
            "or confirm you are using the correct document."
        )
    context = "\n".join(docs)
    first_meta = metadatas[0] if metadatas else {}
    actual_name = first_meta.get("name", "") if isinstance(first_meta, dict) else ""
    today = datetime.date.today().strftime("%B %d, %Y")

    messages=[
            {
                "role": "system",
                "content": f"""Today's date is {today}.
You are answering questions about {actual_name}'s resume.                
Answer ONLY using the context provided.
List ONLY direct employers where the person was PAID to work.
Do NOT include: universities, colleges, educational institutions, clients, partner companies.
A company mentioned as a CLIENT in a job description is NOT an employer.
An institution where the person STUDIED is NOT an employer.
If the answer is not in the context, say 'I don't have enough information'."""},
            {"role": "user", "content": f"Resume context:\n{context}"},
        ]
    # Add conversation history
    messages.extend(safe_history)
    messages.append({"role": "user", "content": question})
    response = llm_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0,
    )
    print(f"Total chunks retrieved: {len(docs)}")
    for i, doc in enumerate(docs):
        print(f"\n--- Chunk {i+1} ---")
        print(doc[:200])
    answer = response.choices[0].message.content    
    redis_client.set(cache_key, answer, ex=3600)
    print("✅ Cache updated!")
    return answer


def clear_answer_cache(pdf_id: str | None = None) -> int:
    if not pdf_id:
        return redis_client.flushdb()

    deleted = 0
    cursor = 0
    pattern = f"{pdf_id}_*"
    while True:
        cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=500)
        if keys:
            deleted += redis_client.delete(*keys)
        if cursor == 0:
            break
    return deleted


def find_pdf_by_contact(
    email: typing.Optional[str] = None,
    name: typing.Optional[str] = None,
    phone: typing.Optional[str] = None,
) -> typing.Optional[str]:
    candidates: list[set[str]] = []

    if email:
        email_rows = collection.get(where={"email": email}, include=["metadatas"])
        email_ids = {
            meta.get("pdf_id")
            for meta in (email_rows.get("metadatas") or [])
            if isinstance(meta, dict) and meta.get("pdf_id")
        }
        candidates.append(set(email_ids))

    if name:
        name_rows = collection.get(where={"name": name}, include=["metadatas"])
        name_ids = {
            meta.get("pdf_id")
            for meta in (name_rows.get("metadatas") or [])
            if isinstance(meta, dict) and meta.get("pdf_id")
        }
        candidates.append(set(name_ids))

    if phone:
        normalized_phone = _digits_only(phone)
        phone_rows = collection.get(where={"phone": normalized_phone}, include=["metadatas"])
        phone_ids = {
            meta.get("pdf_id")
            for meta in (phone_rows.get("metadatas") or [])
            if isinstance(meta, dict) and meta.get("pdf_id")
        }
        candidates.append(set(phone_ids))

    if not candidates:
        return None

    common = candidates[0]
    for candidate_set in candidates[1:]:
        common = common.intersection(candidate_set)
    if common:
        return next(iter(common))

    return None
