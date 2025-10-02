"""
MedGraph AI - FastAPI Main Application
Multi-Agent Medical Records Assistant
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.schemas import (
    QueryRequest,
    QueryResponse,
    PatientInfo,
    MedicalRecord,
    PatientRecordsResponse,
    HealthResponse,
    Citation,
    AgentTrace
)
from app.graph.workflow import MedicalRecordsWorkflow
from app.database.db import get_all_patients, get_patient_records

# Initialize FastAPI app
app = FastAPI(
    title="MedGraph AI",
    description="Multi-Agent Medical Records Assistant with RAG",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize workflow (lazy loading)
workflow = None

def get_workflow():
    """Lazy load the workflow"""
    global workflow
    if workflow is None:
        print("🔄 Initializing MedGraph AI workflow...")
        workflow = MedicalRecordsWorkflow()
        print("✅ Workflow ready!")
    return workflow

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("=" * 60)
    print("🏥 MEDGRAPH AI - STARTING UP")
    print("=" * 60)
    # Preload workflow
    get_workflow()
    print("✅ Server ready!")
    print("📖 API Docs: http://localhost:8000/docs")
    print("=" * 60)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to MedGraph AI",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Check if workflow can be loaded
        wf = get_workflow()
        models_loaded = wf is not None
        
        # Check if database is accessible
        patients = get_all_patients()
        db_connected = len(patients) > 0
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            models_loaded=models_loaded,
            database_connected=db_connected
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            models_loaded=False,
            database_connected=False
        )

@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_medical_records(request: QueryRequest):
    """
    Query medical records using natural language
    
    This endpoint uses 5 AI agents to:
    1. Route the query to appropriate workflow
    2. Retrieve relevant medical records
    3. Build structured context
    4. Extract citations with evidence
    5. Generate a natural language answer
    """
    try:
        # Get workflow
        wf = get_workflow()
        
        # Execute query
        result = wf.query(
            question=request.question,
            patient_id=request.patient_id,
            max_sources=request.max_sources
        )
        
        # Format citations
        citations = [
            Citation(**citation) for citation in result['citations']
        ]
        
        # Format agent trace
        agent_trace = AgentTrace(**result['agent_trace'])
        
        return QueryResponse(
            answer=result['answer'],
            citations=citations,
            agent_trace=agent_trace
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/patients", response_model=list[PatientInfo], tags=["Patients"])
async def list_patients():
    """
    Get list of all patients in the database
    """
    try:
        patients = get_all_patients()
        return [
            PatientInfo(patient_id=p[0], patient_name=p[1])
            for p in patients
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving patients: {str(e)}"
        )

@app.get("/patients/{patient_id}/records", response_model=PatientRecordsResponse, tags=["Patients"])
async def get_patient_records_endpoint(patient_id: str):
    """
    Get all medical records for a specific patient
    """
    try:
        records = get_patient_records(patient_id)
        
        if not records:
            raise HTTPException(
                status_code=404,
                detail=f"No records found for patient {patient_id}"
            )
        
        # Format records
        formatted_records = []
        patient_name = ""
        
        for record in records:
            if not patient_name:
                patient_name = record[2]
            
            formatted_records.append(
                MedicalRecord(
                    id=record[0],
                    patient_id=record[1],
                    patient_name=record[2],
                    date=record[3],
                    record_type=record[4],
                    description=record[5],
                    medication=record[6],
                    diagnosis=record[7],
                    lab_result=record[8],
                    doctor=record[9]
                )
            )
        
        return PatientRecordsResponse(
            patient_id=patient_id,
            patient_name=patient_name,
            total_records=len(formatted_records),
            records=formatted_records
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving records: {str(e)}"
        )

@app.get("/agents", tags=["System"])
async def list_agents():
    """
    List all available agents and their information
    """
    wf = get_workflow()
    
    return {
        "total_agents": 5,
        "agents": [
            wf.router_agent.get_agent_info(),
            wf.retrieval_agent.get_agent_info(),
            wf.context_builder_agent.get_agent_info(),
            wf.citation_agent.get_agent_info(),
            wf.answer_agent.get_agent_info()
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Run the server
if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    
    def open_browser():
        """Open browser after server starts"""
        import time
        time.sleep(2)  # Wait for server to start
        webbrowser.open('http://localhost:8000/docs')
    
    print("\n" + "=" * 60)
    print("🚀 Starting MedGraph AI Server")
    print("=" * 60)
    print("\n📖 API Documentation will open automatically...")
    print("   If not, visit: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    
    # Open browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )