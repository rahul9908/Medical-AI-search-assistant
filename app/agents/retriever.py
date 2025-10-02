"""
Agent 2: Retrieval Agent
Performs hybrid search across medical records using both vector and keyword search
"""
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.db import (
    search_records_vector,
    search_records_sqlite,
    get_patient_records
)

class RetrievalAgent:
    """
    Retrieval Agent performs hybrid search combining:
    1. Vector similarity search (semantic)
    2. Keyword search (exact matching)
    """
    
    def __init__(self):
        """Initialize the retrieval agent"""
        self.name = "Retrieval Agent"
        
    def retrieve(
        self, 
        question: str, 
        patient_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant medical records using hybrid search
        
        Args:
            question: The query question
            patient_id: Optional patient ID to filter results
            top_k: Number of results to return
            
        Returns:
            List of relevant records with metadata
        """
        
        results = []
        
        try:
            # Method 1: Vector search (semantic similarity)
            vector_results = search_records_vector(question, top_k=top_k)
            
            if vector_results and vector_results['documents']:
                for i, doc in enumerate(vector_results['documents'][0]):
                    metadata = vector_results['metadatas'][0][i]
                    distance = vector_results['distances'][0][i] if 'distances' in vector_results else 0
                    
                    # Filter by patient_id if provided
                    if patient_id and metadata.get('patient_id') != patient_id:
                        continue
                    
                    # Calculate confidence score (inverse of distance)
                    confidence = max(0, 1 - distance)
                    
                    results.append({
                        'source_id': vector_results['ids'][0][i],
                        'text': doc,
                        'patient_id': metadata.get('patient_id', ''),
                        'patient_name': metadata.get('patient_name', ''),
                        'date': metadata.get('date', ''),
                        'record_type': metadata.get('record_type', ''),
                        'diagnosis': metadata.get('diagnosis', ''),
                        'medication': metadata.get('medication', ''),
                        'confidence': confidence,
                        'search_method': 'vector'
                    })
            
            # Method 2: If patient_id is specified, get all their records
            if patient_id:
                patient_records = get_patient_records(patient_id)
                
                for record in patient_records[:3]:  # Take top 3 patient-specific records
                    # Check if already in results
                    if not any(r['patient_id'] == record[1] and r['date'] == record[3] for r in results):
                        results.append({
                            'source_id': f"sqlite_{record[0]}",
                            'text': self._format_record(record),
                            'patient_id': record[1],
                            'patient_name': record[2],
                            'date': record[3],
                            'record_type': record[4],
                            'diagnosis': record[6] or '',
                            'medication': record[5] or '',
                            'confidence': 0.85,
                            'search_method': 'patient_filter'
                        })
            
            # Sort by confidence and limit to top_k
            results = sorted(results, key=lambda x: x['confidence'], reverse=True)[:top_k]
            
            return results
            
        except Exception as e:
            print(f"Error in retrieval agent: {e}")
            return []
    
    def _format_record(self, record: tuple) -> str:
        """Format a SQLite record tuple into readable text"""
        return f"""
        Patient: {record[2]} (ID: {record[1]})
        Date: {record[3]}
        Type: {record[4]}
        Description: {record[5] or 'N/A'}
        Diagnosis: {record[6] or 'N/A'}
        Medication: {record[7] or 'N/A'}
        Lab Results: {record[8] or 'N/A'}
        Doctor: {record[9]}
        """.strip()
    
    def get_agent_info(self) -> Dict[str, str]:
        """Return information about this agent"""
        return {
            "name": "Retrieval Agent",
            "role": "Information Retrieval",
            "description": "Performs hybrid search using vector similarity and keyword matching"
        }

# Test the agent
if __name__ == "__main__":
    agent = RetrievalAgent()
    
    test_queries = [
        ("What medications is John Doe taking?", "P001"),
        ("Show me patients with diabetes", None),
        ("Lab results for Robert Wilson", "P003"),
    ]
    
    print("Testing Retrieval Agent:")
    print("=" * 60)
    
    for question, patient_id in test_queries:
        print(f"\nQuestion: {question}")
        if patient_id:
            print(f"Patient Filter: {patient_id}")
        
        results = agent.retrieve(question, patient_id, top_k=3)
        
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n  Result {i}:")
            print(f"    Patient: {result['patient_name']} ({result['patient_id']})")
            print(f"    Date: {result['date']}")
            print(f"    Confidence: {result['confidence']:.2f}")
            print(f"    Method: {result['search_method']}")