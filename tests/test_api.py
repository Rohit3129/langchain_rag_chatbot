from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
import app.main as main_module

client = TestClient(app)

# Test 1: health endpoint works
def test_health():
    r = client.get("/")
    assert r.status_code == 200
    assert "status" in r.json()

# Test 2: /ask returns 503 if chain is None
def test_ask_chain_not_ready():
    orig = main_module.chain
    main_module.chain = None
    r = client.post("/ask", json={"question": "hello"})
    assert r.status_code == 503
    main_module.chain = orig

# Test 3: /ask returns 400 for blank question
def test_ask_empty_question():
    main_module.chain = MagicMock()
    r = client.post("/ask", json={"question": "   "})
    assert r.status_code == 400

# Test 4: /ask returns answer + latency when chain works
def test_ask_success():
    mock = MagicMock()
    mock.invoke.return_value = {"result": "This is the answer"}
    main_module.chain = mock
    r = client.post("/ask", json={"question": "what is this about?"})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert "latency_ms" in data