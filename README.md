# 🏥 MedGraph AI - Multi-Agent Medical Records Assistant

An intelligent assistant powered by **5 specialized AI agents** using **Retrieval-Augmented Generation (RAG)** to answer questions about patient medical history with **grounded citations**.

---

## 🎯 Features

- **5 AI Agents** orchestrated with LangGraph  
- **Hybrid Search**: Semantic (vector) + keyword-based retrieval  
- **Citation System**: Every answer backed by source evidence  
- **Local LLM**: Runs with [Ollama](https://ollama.com) (Mistral) — no API costs  
- **FastAPI** backend with auto-generated docs  
- **50 Synthetic Patient Records** for realistic demo scenarios  

---

## 🏗️ Architecture

User Query
↓
[1. Router Agent] → Classifies query type
↓
[2. Retrieval Agent] → Hybrid search (Vector + SQL)
↓
[3. Context Builder] → Organizes retrieved results
↓
[4. Citation Agent] → Extracts supporting evidence
↓
[5. Answer Agent] → Generates final response
↓
JSON Response with Citations

yaml
Copy code

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.10+)  
- **AI/ML**: LangChain, LangGraph, Sentence Transformers  
- **LLM**: Ollama (Mistral)  
- **Databases**: SQLite (structured) + ChromaDB (vector search)  
- **Testing**: Pytest  

---

## 📦 Project Structure

```bash
medgraph-ai/
├── app/
│   ├── main.py                 # FastAPI entrypoint
│   ├── schemas.py              # Pydantic models
│   ├── agents/
│   │   ├── router.py           # Agent 1: Query router
│   │   ├── retriever.py        # Agent 2: Retrieval logic
│   │   ├── context_builder.py  # Agent 3: Context builder
│   │   ├── citation.py         # Agent 4: Evidence extraction
│   │   └── answer.py           # Agent 5: Final response
│   ├── graph/
│   │   └── workflow.py         # LangGraph orchestration
│   └── database/
│       └── db.py               # SQLite + ChromaDB integration
├── data/
│   ├── medical_records.csv     # Synthetic dataset (50 patients)
│   └── load_data.py            # Data ingestion & embedding
├── tests/
│   └── test_api.py             # Pytest-based tests
├── requirements.txt
└── README.md


---

## Quick Start

### Prerequisites
- Python 3.10 or 3.11  
- Ollama installed (`mistral:latest` pulled)  
- 4GB+ RAM  

### 1. Install Ollama
**Windows**  
- [Download Ollama](https://ollama.com/download/windows)  
- Run:  
```bash
ollama pull mistral:latest
Mac/Linux

bash
Copy code
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral:latest
2. Setup Project
bash
Copy code
# Clone & navigate
cd medgraph-ai

# Create virtual environment
python -m venv medgraph-ai-venv

# Activate
# Windows:
medgraph-ai-venv\Scripts\activate
# Mac/Linux:
source medgraph-ai-venv/bin/activate

# Install dependencies
pip install -r requirements.txt
3. Load Data
bash
Copy code
python data/load_data.py
This will:

Create SQLite DB with 50 patient records

Generate embeddings & build ChromaDB store

Output: "DATA LOADING COMPLETE!"

4. Start Server
bash
Copy code
python app/main.py
Server: http://localhost:8000

API Docs: http://localhost:8000/docs

API Endpoints
Health Check

http
Copy code
GET /health
List Patients

http
Copy code
GET /patients
Get Patient Records

http
Copy code
GET /patients/{patient_id}/records
Query Records (Main Endpoint)

http
Copy code
POST /query
Content-Type: application/json

{
  "question": "What medications is John Doe taking?",
  "patient_id": "P001",
  "max_sources": 5
}
Sample Response

json
Copy code
{
  "answer": "John Doe is currently taking Lisinopril 10mg daily...",
  "citations": [
    {
      "source_id": "record_0",
      "patient_id": "P001",
      "patient_name": "John Doe",
      "date": "2024-07-18",
      "record_type": "visit",
      "text": "Annual physical. Patient continues Lisinopril 10mg daily...",
      "confidence": 0.95
    }
  ],
  "agent_trace": {
    "router_decision": "MEDICATION",
    "agents_used": ["router", "retriever", "context_builder", "citation", "answer"],
    "retrieval_time_ms": 145,
    "total_time_ms": 2340
  }
}
Testing
Run all tests:

bash
Copy code
pytest tests/test_api.py -v
Run individual modules:

bash
Copy code
python app/agents/router.py
python app/agents/retriever.py
python app/graph/workflow.py
Example Queries
Medication

json
Copy code
{ "question": "What medications is John Doe taking?", "patient_id": "P001" }
Diagnosis Lookup

json
Copy code
{ "question": "Show me all patients with diabetes" }
Lab Results

json
Copy code
{ "question": "What were Robert Wilson's latest lab results?", "patient_id": "P003" }
Timeline

json
Copy code
{ "question": "When was Maria Garcia's last visit?", "patient_id": "P004" }
General Health

json
Copy code
{ "question": "Tell me about Jennifer Taylor's mental health treatment" }
How It Works
Router Agent → Classifies query (Medication, Diagnosis, Labs, Timeline, General)

Retrieval Agent → Hybrid search: ChromaDB (semantic) + SQLite (keyword)

Context Builder → Sorts chronologically & filters relevant context

Citation Agent → Extracts evidence & assigns confidence scores

Answer Agent → Generates structured, evidence-based response via Mistral

Sample Dataset
Includes 50 synthetic records for 10 demo patients:

P001: John Doe (Hypertension)

P002: Jane Smith (Bronchitis)

P003: Robert Wilson (Diabetes Type 2)

P004: Maria Garcia (Allergic Rhinitis)

P005: Michael Brown (Back Pain)

P006: Jennifer Taylor (Depression)

P007: David Martinez (Asthma)

P008: Linda Anderson (Hypothyroidism)

P009: Christopher Lee (Knee Sprain)

P010: Patricia White (GERD)

Troubleshooting
Ollama connection refused → Run ollama serve & check ollama list

No module named 'app' → Activate virtual environment & run from root dir

Database not found → Re-run python data/load_data.py

Slow response → First call is slower; use smaller models if needed

Future Enhancements
Expand dataset with more patients

Add caching for faster queries

Streaming responses

Support for medical images

Multi-turn conversation support

Fine-tuned embeddings on medical corpora

GraphQL API

Docker deployment

License
This project is for educational purposes only.

Author
Rahul Tammalla
Built as a demonstration of multi-agent RAG systems for healthcare.

yaml
Copy code
