"""
Agent 1: Router Agent
Routes queries to appropriate processing workflow
"""
from langchain_community.llms import Ollama
from typing import Dict

class RouterAgent:
    """
    Router Agent classifies the type of medical query and determines
    which agents should process it.
    """
    
    def __init__(self, model_name: str = "mistral:latest"):
        """Initialize the router agent with Ollama model"""
        self.llm = Ollama(model=model_name, temperature=0.1)
        
    def route(self, question: str) -> Dict[str, any]:
        """
        Route the question to appropriate workflow
        
        Returns:
            Dict with routing decision and metadata
        """
        
        prompt = f"""You are a medical query router. Classify the following question into ONE category:

Categories:
1. MEDICATION - Questions about medications, prescriptions, drug names
2. DIAGNOSIS - Questions about diagnoses, conditions, diseases
3. LAB_RESULTS - Questions about lab tests, test results, measurements
4. TIMELINE - Questions about medical history, visit dates, chronological events
5. GENERAL - General questions about patient health or multiple topics

Question: {question}

Respond with ONLY the category name (e.g., MEDICATION).
Category:"""

        try:
            response = self.llm.invoke(prompt).strip().upper()
            
            # Extract category from response
            categories = ["MEDICATION", "DIAGNOSIS", "LAB_RESULTS", "TIMELINE", "GENERAL"]
            
            for category in categories:
                if category in response:
                    return {
                        "category": category,
                        "confidence": 0.9,
                        "reasoning": f"Query classified as {category}"
                    }
            
            # Default to GENERAL if unclear
            return {
                "category": "GENERAL",
                "confidence": 0.5,
                "reasoning": "Could not clearly classify query"
            }
            
        except Exception as e:
            print(f"Error in router agent: {e}")
            return {
                "category": "GENERAL",
                "confidence": 0.3,
                "reasoning": f"Error during routing: {str(e)}"
            }
    
    def get_agent_info(self) -> Dict[str, str]:
        """Return information about this agent"""
        return {
            "name": "Router Agent",
            "role": "Query Classification",
            "description": "Classifies incoming queries and routes them to appropriate workflows"
        }

# Test the agent
if __name__ == "__main__":
    agent = RouterAgent()
    
    test_questions = [
        "What medications is John Doe taking?",
        "Show me all patients with diabetes",
        "What were the latest lab results for Patient P003?",
        "When was Maria Garcia's last visit?",
    ]
    
    print("Testing Router Agent:")
    print("=" * 60)
    
    for question in test_questions:
        result = agent.route(question)
        print(f"\nQuestion: {question}")
        print(f"Category: {result['category']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Reasoning: {result['reasoning']}")