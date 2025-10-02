"""
Test suite for MedGraph AI API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["version"] == "1.0.0"

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "unhealthy"]
    assert "version" in data

def test_list_patients():
    """Test listing all patients"""
    response = client.get("/patients")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check structure
    if data:
        assert "patient_id" in data[0]
        assert "patient_name" in data[0]

def test_get_patient_records():
    """Test getting records for a specific patient"""
    # First get a patient ID
    patients_response = client.get("/patients")
    patients = patients_response.json()
    
    if patients:
        patient_id = patients[0]["patient_id"]
        
        # Get records for this patient
        response = client.get(f"/patients/{patient_id}/records")
        assert response.status_code == 200
        data = response.json()
        assert "patient_id" in data
        assert "records" in data
        assert isinstance(data["records"], list)

def test_query_endpoint():
    """Test the main query endpoint"""
    query_data = {
        "question": "What medications is John Doe taking?",
        "patient_id": "P001",
        "max_sources": 5
    }
    
    response = client.post("/query", json=query_data)
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "answer" in data
    assert "citations" in data
    assert "agent_trace" in data
    
    # Check agent trace
    assert "router_decision" in data["agent_trace"]
    assert "agents_used" in data["agent_trace"]
    assert len(data["agent_trace"]["agents_used"]) == 5  # All 5 agents

def test_query_without_patient_filter():
    """Test query without patient ID filter"""
    query_data = {
        "question": "Show me patients with hypertension",
        "max_sources": 5
    }
    
    response = client.post("/query", json=query_data)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data

def test_list_agents():
    """Test listing all agents"""
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    assert data["total_agents"] == 5
    assert "agents" in data
    assert len(data["agents"]) == 5

def test_invalid_patient_id():
    """Test with invalid patient ID"""
    response = client.get("/patients/INVALID999/records")
    assert response.status_code == 404

def test_malformed_query():
    """Test with malformed query request"""
    response = client.post("/query", json={})
    assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    print("Running MedGraph AI Tests...")
    print("=" * 60)
    
    # Run tests manually
    test_root_endpoint()
    print("✅ Root endpoint test passed")
    
    test_health_check()
    print("✅ Health check test passed")
    
    test_list_patients()
    print("✅ List patients test passed")
    
    test_get_patient_records()
    print("✅ Get patient records test passed")
    
    test_list_agents()
    print("✅ List agents test passed")
    
    test_invalid_patient_id()
    print("✅ Invalid patient ID test passed")
    
    test_malformed_query()
    print("✅ Malformed query test passed")
    
    print("\n" + "=" * 60)
    print("Running full query test (this takes longer)...")
    test_query_endpoint()
    print("✅ Query endpoint test passed")
    
    test_query_without_patient_filter()
    print("✅ Query without filter test passed")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)