"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Request Models
class QueryRequest(BaseModel):
    """Request model for querying medical records"""
    question: str = Field(..., description="The question to ask about medical records")
    patient_id: Optional[str] = Field(None, description="Optional patient ID to filter results")
    max_sources: int = Field(5, description="Maximum number of source documents to retrieve")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What medications is John Doe taking?",
                "patient_id": "P001",
                "max_sources": 5
            }
        }

# Response Models
class Citation(BaseModel):
    """Citation model for source references"""
    source_id: str = Field(..., description="Unique identifier for the source")
    patient_id: str = Field(..., description="Patient ID")
    patient_name: str = Field(..., description="Patient name")
    date: str = Field(..., description="Date of the record")
    record_type: str = Field(..., description="Type of medical record")
    text: str = Field(..., description="Relevant text from the source")
    confidence: float = Field(..., description="Confidence score (0-1)")

class AgentTrace(BaseModel):
    """Trace information about which agents were used"""
    router_decision: str = Field(..., description="Decision made by router agent")
    agents_used: List[str] = Field(..., description="List of agents that processed the query")
    retrieval_time_ms: int = Field(..., description="Time taken for retrieval in milliseconds")
    total_time_ms: int = Field(..., description="Total processing time in milliseconds")

class QueryResponse(BaseModel):
    """Response model for medical record queries"""
    answer: str = Field(..., description="The generated answer to the question")
    citations: List[Citation] = Field(..., description="List of source citations")
    agent_trace: AgentTrace = Field(..., description="Information about agent processing")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "John Doe is currently taking Lisinopril 10mg daily for hypertension management.",
                "citations": [
                    {
                        "source_id": "record_0",
                        "patient_id": "P001",
                        "patient_name": "John Doe",
                        "date": "2024-01-15",
                        "record_type": "visit",
                        "text": "Patient presents with elevated blood pressure. Prescribed Lisinopril 10mg daily.",
                        "confidence": 0.95
                    }
                ],
                "agent_trace": {
                    "router_decision": "medication_query",
                    "agents_used": ["router", "retriever", "context_builder", "citation", "answer"],
                    "retrieval_time_ms": 145,
                    "total_time_ms": 2340
                }
            }
        }

# Patient Models
class PatientInfo(BaseModel):
    """Patient information model"""
    patient_id: str
    patient_name: str

class MedicalRecord(BaseModel):
    """Medical record model"""
    id: int
    patient_id: str
    patient_name: str
    date: str
    record_type: str
    description: Optional[str]
    medication: Optional[str]
    diagnosis: Optional[str]
    lab_result: Optional[str]
    doctor: str

class PatientRecordsResponse(BaseModel):
    """Response model for patient records"""
    patient_id: str
    patient_name: str
    total_records: int
    records: List[MedicalRecord]

# Health Check Model
class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    models_loaded: bool = Field(..., description="Whether AI models are loaded")
    database_connected: bool = Field(..., description="Whether database is accessible")