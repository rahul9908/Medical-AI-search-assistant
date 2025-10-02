\# 🏥 MedGraph AI - Multi-Agent Medical Records Assistant



An intelligent medical records assistant powered by 5 specialized AI agents using RAG (Retrieval-Augmented Generation) to answer questions about patient medical history with proper citations.



\## 🎯 Features



\- \*\*5 AI Agents\*\* orchestrated with LangGraph

\- \*\*Hybrid Search\*\* - Combines semantic (vector) and keyword search

\- \*\*Citation System\*\* - Every answer backed by source evidence

\- \*\*Local LLM\*\* - Uses Ollama (Mistral) - no API costs

\- \*\*FastAPI\*\* - Modern, fast REST API with auto-generated docs

\- \*\*50 Patient Records\*\* - Realistic synthetic medical data



\## 🏗️ Architecture



```

User Query

&nbsp;   ↓

\[1. Router Agent] ← Classifies query type

&nbsp;   ↓

\[2. Retrieval Agent] ← Hybrid search (Vector + SQL)

&nbsp;   ↓

\[3. Context Builder] ← Organizes results

&nbsp;   ↓

\[4. Citation Agent] ← Extracts evidence

&nbsp;   ↓

\[5. Answer Agent] ← Generates response

&nbsp;   ↓

JSON Response with Citations

```



\## 🛠️ Tech Stack



\- \*\*Backend\*\*: FastAPI (Python 3.10+)

\- \*\*AI/ML\*\*: LangChain, LangGraph, Sentence Transformers

\- \*\*LLM\*\*: Ollama (Mistral)

\- \*\*Databases\*\*: SQLite (structured) + ChromaDB (vector)

\- \*\*Testing\*\*: Pytest



\## 📦 Project Structure



```

medgraph-ai/

├── app/

│   ├── main.py                 # FastAPI application

│   ├── schemas.py              # Pydantic models

│   ├── agents/

│   │   ├── router.py           # Agent 1: Query router

│   │   ├── retriever.py        # Agent 2: Record retrieval

│   │   ├── context\_builder.py # Agent 3: Context organization

│   │   ├── citation.py         # Agent 4: Evidence extraction

│   │   └── answer.py           # Agent 5: Answer generation

│   ├── graph/

│   │   └── workflow.py         # LangGraph orchestration

│   └── database/

│       └── db.py               # Database operations

├── data/

│   ├── medical\_records.csv     # 50 patient records

│   └── load\_data.py            # Data loading script

├── tests/

│   └── test\_api.py             # API tests

├── requirements.txt

└── README.md

```



\## 🚀 Quick Start



\### Prerequisites



\- Python 3.10 or 3.11

\- Ollama installed

\- 4GB+ RAM



\### 1. Install Ollama



\*\*Windows:\*\*

\- Download from: https://ollama.com/download/windows

\- Install and run: `ollama pull mistral:latest`



\*\*Mac/Linux:\*\*

```bash

curl -fsSL https://ollama.com/install.sh | sh

ollama pull mistral:latest

```



\### 2. Setup Project



```bash

\# Clone/navigate to project

cd medgraph-ai



\# Create virtual environment

python -m venv medgraph-ai-venv



\# Activate virtual environment

\# Windows:

medgraph-ai-venv\\Scripts\\activate

\# Mac/Linux:

source medgraph-ai-venv/bin/activate



\# Install dependencies

pip install -r requirements.txt

```



\### 3. Load Data



```bash

python data/load\_data.py

```



This will:

\- Create SQLite database with 50 medical records

\- Generate embeddings for semantic search

\- Create ChromaDB vector store



Expected output: "✅ DATA LOADING COMPLETE!"



\### 4. Start the Server



```bash

python app/main.py

```



Server will start at: \*\*http://localhost:8000\*\*



API Documentation: \*\*http://localhost:8000/docs\*\*



\## 📖 API Endpoints



\### Health Check

```bash

GET /health

```



\### List All Patients

```bash

GET /patients

```



\### Get Patient Records

```bash

GET /patients/{patient\_id}/records

```



\### Query Medical Records (Main Endpoint)

```bash

POST /query

Content-Type: application/json



{

&nbsp; "question": "What medications is John Doe taking?",

&nbsp; "patient\_id": "P001",

&nbsp; "max\_sources": 5

}

```



\*\*Response:\*\*

```json

{

&nbsp; "answer": "John Doe is currently taking Lisinopril 10mg daily...",

&nbsp; "citations": \[

&nbsp;   {

&nbsp;     "source\_id": "record\_0",

&nbsp;     "patient\_id": "P001",

&nbsp;     "patient\_name": "John Doe",

&nbsp;     "date": "2024-07-18",

&nbsp;     "record\_type": "visit",

&nbsp;     "text": "Annual physical. Patient continues Lisinopril 10mg daily...",

&nbsp;     "confidence": 0.95

&nbsp;   }

&nbsp; ],

&nbsp; "agent\_trace": {

&nbsp;   "router\_decision": "MEDICATION",

&nbsp;   "agents\_used": \["router", "retriever", "context\_builder", "citation", "answer"],

&nbsp;   "retrieval\_time\_ms": 145,

&nbsp;   "total\_time\_ms": 2340

&nbsp; }

}

```



\## 🧪 Testing



\### Run All Tests

```bash

pytest tests/test\_api.py -v

```



\### Run Manual Test

```bash

python tests/test\_api.py

```



\### Test Individual Agents

```bash

\# Test router agent

python app/agents/router.py



\# Test retrieval agent

python app/agents/retriever.py



\# Test workflow

python app/graph/workflow.py

```



\## 💡 Example Queries



Try these in the Swagger UI (http://localhost:8000/docs):



1\. \*\*Medication Query:\*\*

&nbsp;  ```json

&nbsp;  {

&nbsp;    "question": "What medications is John Doe taking?",

&nbsp;    "patient\_id": "P001"

&nbsp;  }

&nbsp;  ```



2\. \*\*Diagnosis Lookup:\*\*

&nbsp;  ```json

&nbsp;  {

&nbsp;    "question": "Show me all patients with diabetes"

&nbsp;  }

&nbsp;  ```



3\. \*\*Lab Results:\*\*

&nbsp;  ```json

&nbsp;  {

&nbsp;    "question": "What were Robert Wilson's latest lab results?",

&nbsp;    "patient\_id": "P003"

&nbsp;  }

&nbsp;  ```



4\. \*\*Timeline Query:\*\*

&nbsp;  ```json

&nbsp;  {

&nbsp;    "question": "When was Maria Garcia's last visit?",

&nbsp;    "patient\_id": "P004"

&nbsp;  }

&nbsp;  ```



5\. \*\*General Query:\*\*

&nbsp;  ```json

&nbsp;  {

&nbsp;    "question": "Tell me about Jennifer Taylor's mental health treatment"

&nbsp;  }

&nbsp;  ```



\## 🔍 How It Works



\### 1. Router Agent

\- Classifies query into categories: MEDICATION, DIAGNOSIS, LAB\_RESULTS, TIMELINE, GENERAL

\- Uses Mistral LLM with few-shot prompting



\### 2. Retrieval Agent

\- \*\*Semantic Search\*\*: Uses sentence transformers to find similar records (ChromaDB)

\- \*\*Keyword Search\*\*: Exact matching on patient data (SQLite)

\- \*\*Hybrid Fusion\*\*: Combines both methods for best results



\### 3. Context Builder Agent

\- Sorts records chronologically

\- Extracts key findings based on query category

\- Groups related information



\### 4. Citation Agent

\- Extracts relevant text snippets

\- Calculates confidence scores

\- Creates source references



\### 5. Answer Agent

\- Uses Mistral LLM with structured prompt

\- Generates answer ONLY from evidence

\- Formats response professionally



\## 📊 Sample Data



The system includes 50 medical records for 10 patients:

\- \*\*P001\*\*: John Doe (Hypertension)

\- \*\*P002\*\*: Jane Smith (Bronchitis)

\- \*\*P003\*\*: Robert Wilson (Type 2 Diabetes)

\- \*\*P004\*\*: Maria Garcia (Allergic Rhinitis)

\- \*\*P005\*\*: Michael Brown (Back Pain)

\- \*\*P006\*\*: Jennifer Taylor (Depression)

\- \*\*P007\*\*: David Martinez (Asthma)

\- \*\*P008\*\*: Linda Anderson (Hypothyroidism)

\- \*\*P009\*\*: Christopher Lee (Knee Sprain)

\- \*\*P010\*\*: Patricia White (GERD)



\## 🛡️ Troubleshooting



\### "Ollama connection refused"

\- Make sure Ollama is running: `ollama serve`

\- Check model is installed: `ollama list`



\### "No module named 'app'"

\- Make sure virtual environment is activated

\- Verify you're in the project root directory



\### "Database not found"

\- Run data loading script: `python data/load\_data.py`



\### "Slow response times"

\- First query is always slower (model loading)

\- Subsequent queries are much faster

\- Consider using a smaller model for faster responses



\## 🎯 Future Enhancements



\- \[ ] Add more patients and records

\- \[ ] Implement caching for faster responses

\- \[ ] Add streaming responses

\- \[ ] Support for medical images

\- \[ ] Multi-turn conversations

\- \[ ] Fine-tuned embeddings on medical data

\- \[ ] GraphQL API

\- \[ ] Docker deployment



\## 📝 License



This project is for educational purposes.



\## 👨‍💻 Author



Built as a demonstration of multi-agent RAG systems for medical records.



---



