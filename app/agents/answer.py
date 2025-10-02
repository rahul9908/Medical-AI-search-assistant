"""
Agent 5: Answer Agent
Generates final answer using LLM based on context and citations
"""
from langchain_community.llms import Ollama
from typing import Dict, List

class AnswerAgent:
    """
    Answer Agent:
    1. Takes organized context and citations
    2. Uses LLM to generate natural language answer
    3. Ensures answer is grounded in evidence
    4. Formats response professionally
    """
    
    def __init__(self, model_name: str = "mistral:latest"):
        """Initialize the answer agent with Ollama model"""
        self.llm = Ollama(model=model_name, temperature=0.3)
        self.name = "Answer Agent"
    
    def generate_answer(
        self,
        question: str,
        context: Dict,
        citations: List[Dict],
        category: str
    ) -> str:
        """
        Generate final answer based on context and citations
        
        Args:
            question: Original question
            context: Structured context from context builder
            citations: List of citations from citation agent
            category: Query category
            
        Returns:
            Generated answer string
        """
        
        if not citations:
            return "I couldn't find any relevant information in the medical records to answer this question."
        
        # Build the prompt
        prompt = self._build_prompt(question, context, citations, category)
        
        try:
            # Generate answer using LLM
            answer = self.llm.invoke(prompt)
            
            # Clean up the answer
            answer = self._clean_answer(answer)
            
            return answer
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"
    
    def _build_prompt(
        self,
        question: str,
        context: Dict,
        citations: List[Dict],
        category: str
    ) -> str:
        """Build the prompt for the LLM"""
        
        # Format citations as evidence
        evidence = self._format_evidence(citations)
        
        # Create context summary
        summary = context.get('context_summary', '')
        key_findings = context.get('key_findings', [])
        
        prompt = f"""You are a medical records assistant. Answer the question based ONLY on the provided evidence.

Question: {question}

Context Summary: {summary}

Key Findings:
{chr(10).join('- ' + finding for finding in key_findings)}

Evidence from Medical Records:
{evidence}

Instructions:
1. Answer the question directly and concisely
2. Use ONLY information from the evidence provided above
3. Be specific - mention patient names, dates, medications, diagnoses, etc.
4. If the evidence shows conflicting information, mention both
5. If the evidence is insufficient, say so clearly
6. Do NOT make up or infer information not in the evidence
7. Keep your answer focused and under 150 words

Answer:"""

        return prompt
    
    def _format_evidence(self, citations: List[Dict]) -> str:
        """Format citations as evidence text for the prompt"""
        evidence_parts = []
        
        for i, citation in enumerate(citations, 1):
            evidence_part = f"""
[Source {i}]
Patient: {citation['patient_name']} ({citation['patient_id']})
Date: {citation['date']}
Type: {citation['record_type']}
Content: {citation['text']}
"""
            evidence_parts.append(evidence_part.strip())
        
        return "\n\n".join(evidence_parts)
    
    def _clean_answer(self, answer: str) -> str:
        """Clean and format the generated answer"""
        # Remove any leading/trailing whitespace
        answer = answer.strip()
        
        # Remove common artifacts
        answer = answer.replace("Answer:", "").strip()
        answer = answer.replace("Based on the evidence:", "").strip()
        
        # Ensure it starts with a capital letter
        if answer and answer[0].islower():
            answer = answer[0].upper() + answer[1:]
        
        # Remove any incomplete sentences at the end
        if answer and not answer[-1] in '.!?':
            # Find last complete sentence
            last_period = max(
                answer.rfind('.'),
                answer.rfind('!'),
                answer.rfind('?')
            )
            if last_period > len(answer) * 0.5:  # At least 50% of content
                answer = answer[:last_period + 1]
        
        return answer
    
    def get_agent_info(self) -> Dict[str, str]:
        """Return information about this agent"""
        return {
            "name": "Answer Agent",
            "role": "Answer Generation",
            "description": "Generates natural language answers grounded in evidence"
        }

# Test the agent
if __name__ == "__main__":
    agent = AnswerAgent()
    
    # Mock data
    mock_context = {
        'context_summary': "Found 2 records for John Doe. Date range: 2024-03-10 to 2024-07-18.",
        'key_findings': [
            "Medications found: Lisinopril 10mg daily",
            "All records for patient: John Doe"
        ]
    }
    
    mock_citations = [
        {
            'source_id': 'rec1',
            'patient_id': 'P001',
            'patient_name': 'John Doe',
            'date': '2024-07-18',
            'record_type': 'visit',
            'text': 'Annual physical examination. Patient continues Lisinopril 10mg daily for hypertension management. Blood pressure well controlled at 128/82 mmHg.',
            'confidence': 0.95
        }
    ]
    
    print("Testing Answer Agent:")
    print("=" * 60)
    
    answer = agent.generate_answer(
        question="What medications is John Doe taking?",
        context=mock_context,
        citations=mock_citations,
        category="MEDICATION"
    )
    
    print(f"\nGenerated Answer:\n{answer}")