import asyncio, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.rag_chain import build_rag_chain

app = FastAPI(title="RAG Chatbot")
chain = None
history = []
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
    start = time.time()
    answer = await asyncio.get_event_loop().run_in_executor(
        None, lambda: chain.invoke(q.question)
    )
    latency = round((time.time() - start) * 1000, 2)
    history.append({"question": q.question, "answer": answer, "latency_ms": latency})
    return history[-1]  # return the latest entry

# Add new endpoint
@app.get("/history")
async def get_history():
    return {"total": len(history), "history": history}

@app.delete("/history")
async def clear_history():
    history.clear()
    return {"message": "History cleared"}