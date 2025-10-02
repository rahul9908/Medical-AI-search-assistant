"""
Agent 3: Context Builder Agent
Organizes and structures retrieved records into coherent context
"""
from typing import List, Dict
from datetime import datetime

class ContextBuilderAgent:
    """
    Context Builder Agent takes raw retrieval results and:
    1. Organizes them chronologically
    2. Groups related information
    3. Identifies key patterns
    4. Creates structured context for the answer agent
    """
    
    def __init__(self):
        """Initialize the context builder agent"""
        self.name = "Context Builder Agent"
    
    def build_context(
        self, 
        question: str,
        retrieved_records: List[Dict],
        category: str
    ) -> Dict:
        """
        Build structured context from retrieved records
        
        Args:
            question: Original query
            retrieved_records: List of retrieved records
            category: Query category from router
            
        Returns:
            Structured context dictionary
        """
        
        if not retrieved_records:
            return {
                "context_summary": "No relevant records found.",
                "total_records": 0,
                "records": [],
                "key_findings": []
            }
        
        # Sort records by date (most recent first)
        sorted_records = self._sort_by_date(retrieved_records)
        
        # Extract key information based on category
        key_findings = self._extract_key_findings(sorted_records, category)
        
        # Create context summary
        context_summary = self._create_summary(sorted_records, category)
        
        # Group records by patient if multiple patients
        patient_groups = self._group_by_patient(sorted_records)
        
        return {
            "context_summary": context_summary,
            "total_records": len(sorted_records),
            "records": sorted_records,
            "key_findings": key_findings,
            "patient_groups": patient_groups,
            "category": category
        }
    
    def _sort_by_date(self, records: List[Dict]) -> List[Dict]:
        """Sort records by date in descending order"""
        try:
            return sorted(
                records,
                key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'),
                reverse=True
            )
        except:
            # If date parsing fails, return as-is
            return records
    
    def _extract_key_findings(self, records: List[Dict], category: str) -> List[str]:
        """Extract key findings based on query category"""
        findings = []
        
        if category == "MEDICATION":
            medications = set()
            for record in records:
                med = record.get('medication', '').strip()
                if med and med.lower() not in ['none', 'n/a', '']:
                    medications.add(med)
            if medications:
                findings.append(f"Medications found: {', '.join(medications)}")
        
        elif category == "DIAGNOSIS":
            diagnoses = set()
            for record in records:
                diag = record.get('diagnosis', '').strip()
                if diag and diag.lower() not in ['none', 'n/a', '']:
                    diagnoses.add(diag)
            if diagnoses:
                findings.append(f"Diagnoses found: {', '.join(diagnoses)}")
        
        elif category == "TIMELINE":
            if records:
                earliest = records[-1]['date']
                latest = records[0]['date']
                findings.append(f"Records span from {earliest} to {latest}")
                findings.append(f"Total visits/records: {len(records)}")
        
        elif category == "LAB_RESULTS":
            lab_count = sum(1 for r in records if r.get('record_type') == 'lab')
            if lab_count > 0:
                findings.append(f"Found {lab_count} lab result(s)")
        
        # General findings
        patients = set(r['patient_name'] for r in records)
        if len(patients) == 1:
            findings.append(f"All records for patient: {list(patients)[0]}")
        else:
            findings.append(f"Records from {len(patients)} patient(s)")
        
        return findings
    
    def _create_summary(self, records: List[Dict], category: str) -> str:
        """Create a concise summary of the context"""
        num_records = len(records)
        patients = set(r['patient_name'] for r in records)
        
        if len(patients) == 1:
            patient_name = list(patients)[0]
            summary = f"Found {num_records} record(s) for {patient_name}. "
        else:
            summary = f"Found {num_records} record(s) across {len(patients)} patient(s). "
        
        if records:
            date_range = f"Date range: {records[-1]['date']} to {records[0]['date']}."
            summary += date_range
        
        return summary
    
    def _group_by_patient(self, records: List[Dict]) -> Dict[str, List[Dict]]:
        """Group records by patient ID"""
        groups = {}
        for record in records:
            patient_id = record['patient_id']
            if patient_id not in groups:
                groups[patient_id] = []
            groups[patient_id].append(record)
        return groups
    
    def get_agent_info(self) -> Dict[str, str]:
        """Return information about this agent"""
        return {
            "name": "Context Builder Agent",
            "role": "Context Organization",
            "description": "Organizes retrieved records into structured, coherent context"
        }

# Test the agent
if __name__ == "__main__":
    agent = ContextBuilderAgent()
    
    # Mock retrieved records
    mock_records = [
        {
            'source_id': 'rec1',
            'patient_id': 'P001',
            'patient_name': 'John Doe',
            'date': '2024-07-18',
            'record_type': 'visit',
            'diagnosis': 'Hypertension Stage 1',
            'medication': 'Lisinopril 10mg daily',
            'confidence': 0.95
        },
        {
            'source_id': 'rec2',
            'patient_id': 'P001',
            'patient_name': 'John Doe',
            'date': '2024-03-10',
            'record_type': 'visit',
            'diagnosis': 'Hypertension Stage 1',
            'medication': 'Lisinopril 10mg daily',
            'confidence': 0.88
        }
    ]
    
    print("Testing Context Builder Agent:")
    print("=" * 60)
    
    context = agent.build_context(
        question="What medications is John Doe taking?",
        retrieved_records=mock_records,
        category="MEDICATION"
    )
    
    print(f"\nContext Summary: {context['context_summary']}")
    print(f"Total Records: {context['total_records']}")
    print(f"\nKey Findings:")
    for finding in context['key_findings']:
        print(f"  - {finding}")