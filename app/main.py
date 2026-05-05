from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.rag_chain import build_rag_chain

app = FastAPI(title="RAG Chatbot")

chain = None

class Question(BaseModel):
    question: str

@app.on_event("startup")
async def startup():
    global chain
    chain = build_rag_chain("data/sample.pdf")
    print("Chain ready!")

@app.get("/")
async def health():
    return {"status": "ok", "chain_loaded": chain is not None}

@app.post("/ask")
async def ask(q: Question):
    if not chain:
        raise HTTPException(status_code=503, detail="Chain not ready")
    if not q.question.strip():
        raise HTTPException(status_code=400, detail="Empty question")
    answer = chain.invoke(q.question)
    return {"question": q.question, "answer": answer}