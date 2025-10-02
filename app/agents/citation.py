"""
Agent 4: Citation Agent
Extracts evidence and builds citations with confidence scores
"""
from typing import List, Dict
import re

class CitationAgent:
    """
    Citation Agent:
    1. Extracts relevant evidence from records
    2. Creates proper citations
    3. Calculates confidence scores
    4. Links answers to source documents
    """
    
    def __init__(self):
        """Initialize the citation agent"""
        self.name = "Citation Agent"
    
    def create_citations(
        self,
        question: str,
        context: Dict,
        answer_preview: str = None
    ) -> List[Dict]:
        """
        Create citations from context records
        
        Args:
            question: Original question
            context: Context built by context builder agent
            answer_preview: Preview of the answer (to determine relevance)
            
        Returns:
            List of citation dictionaries
        """
        
        citations = []
        records = context.get('records', [])
        
        for record in records:
            citation = self._build_citation(record, question, answer_preview)
            if citation:
                citations.append(citation)
        
        # Sort by confidence
        citations = sorted(citations, key=lambda x: x['confidence'], reverse=True)
        
        return citations
    
    def _build_citation(
        self,
        record: Dict,
        question: str,
        answer_preview: str = None
    ) -> Dict:
        """Build a single citation from a record"""
        
        # Extract the most relevant text snippet
        relevant_text = self._extract_relevant_snippet(record, question)
        
        # Calculate confidence based on multiple factors
        confidence = self._calculate_confidence(record, question, answer_preview)
        
        citation = {
            'source_id': record.get('source_id', 'unknown'),
            'patient_id': record.get('patient_id', ''),
            'patient_name': record.get('patient_name', ''),
            'date': record.get('date', ''),
            'record_type': record.get('record_type', ''),
            'text': relevant_text,
            'confidence': round(confidence, 2)
        }
        
        return citation
    
    def _extract_relevant_snippet(self, record: Dict, question: str) -> str:
        """
        Extract the most relevant text snippet from a record
        """
        # Get the full text
        full_text = record.get('text', '')
        
        # Try to find the most relevant sentence
        # Look for key terms from the question
        question_lower = question.lower()
        
        # Extract key terms (simple approach)
        key_terms = [
            'medication', 'diagnosis', 'lab', 'result', 'test',
            'prescribed', 'treatment', 'condition', 'visit'
        ]
        
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', full_text)
        
        # Find sentences containing relevant information
        relevant_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check for question terms or key medical terms
            if any(term in question_lower and term in sentence_lower for term in key_terms):
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            # Return the most relevant sentence(s)
            snippet = '. '.join(relevant_sentences[:2])  # Max 2 sentences
        else:
            # Fall back to description or first part of text
            if 'Description:' in full_text:
                desc_match = re.search(r'Description:\s*([^\n]+)', full_text)
                if desc_match:
                    snippet = desc_match.group(1).strip()
                else:
                    snippet = full_text[:200]  # First 200 chars
            else:
                snippet = full_text[:200]
        
        return snippet
    
    def _calculate_confidence(
        self,
        record: Dict,
        question: str,
        answer_preview: str = None
    ) -> float:
        """
        Calculate confidence score for a citation
        
        Factors:
        1. Base confidence from retrieval
        2. Recency of record
        3. Relevance to question keywords
        4. Record type relevance
        """
        
        # Start with retrieval confidence
        base_confidence = record.get('confidence', 0.7)
        
        # Boost for direct relevance
        relevance_boost = 0.0
        question_lower = question.lower()
        record_text = record.get('text', '').lower()
        
        # Check for keyword matches
        if 'medication' in question_lower and record.get('medication'):
            relevance_boost += 0.1
        if 'diagnosis' in question_lower and record.get('diagnosis'):
            relevance_boost += 0.1
        if 'lab' in question_lower and record.get('record_type') == 'lab':
            relevance_boost += 0.15
        
        # Recency boost (2024 records are more relevant)
        date = record.get('date', '')
        if '2024' in date:
            month = int(date.split('-')[1]) if '-' in date else 1
            # More recent months get higher boost
            recency_boost = (month / 12) * 0.1
        else:
            recency_boost = 0.0
        
        # Calculate final confidence (cap at 1.0)
        final_confidence = min(1.0, base_confidence + relevance_boost + recency_boost)
        
        return final_confidence
    
    def format_citations_for_display(self, citations: List[Dict]) -> str:
        """Format citations as readable text"""
        if not citations:
            return "No citations available."
        
        formatted = "Sources:\n"
        for i, citation in enumerate(citations, 1):
            formatted += f"\n[{i}] {citation['patient_name']} - {citation['date']}\n"
            formatted += f"    {citation['text']}\n"
            formatted += f"    (Confidence: {citation['confidence']:.0%})\n"
        
        return formatted
    
    def get_agent_info(self) -> Dict[str, str]:
        """Return information about this agent"""
        return {
            "name": "Citation Agent",
            "role": "Evidence Extraction",
            "description": "Extracts evidence and creates citations with confidence scores"
        }

# Test the agent
if __name__ == "__main__":
    agent = CitationAgent()
    
    # Mock context
    mock_context = {
        'records': [
            {
                'source_id': 'rec1',
                'patient_id': 'P001',
                'patient_name': 'John Doe',
                'date': '2024-07-18',
                'record_type': 'visit',
                'text': 'Patient presents with hypertension. Prescribed Lisinopril 10mg daily.',
                'diagnosis': 'Hypertension Stage 1',
                'medication': 'Lisinopril 10mg daily',
                'confidence': 0.95
            }
        ]
    }
    
    print("Testing Citation Agent:")
    print("=" * 60)
    
    citations = agent.create_citations(
        question="What medications is John Doe taking?",
        context=mock_context
    )
    
    print(f"\nCreated {len(citations)} citation(s):")
    print(agent.format_citations_for_display(citations))