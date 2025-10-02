"""
LangGraph Workflow - Orchestrates all 5 agents
"""
import sys
from pathlib import Path
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.agents.router import RouterAgent
from app.agents.retriever import RetrievalAgent
from app.agents.context_builder import ContextBuilderAgent
from app.agents.citation import CitationAgent
from app.agents.answer import AnswerAgent

# Define the state that flows through the graph
class AgentState(TypedDict):
    """State that gets passed between agents"""
    question: str
    patient_id: str
    max_sources: int
    
    # Agent outputs
    router_result: Dict
    retrieved_records: List[Dict]
    context: Dict
    citations: List[Dict]
    final_answer: str
    
    # Metadata
    agents_used: List[str]
    start_time: float
    retrieval_time_ms: int
    total_time_ms: int

class MedicalRecordsWorkflow:
    """
    Workflow that orchestrates all 5 agents in sequence:
    1. Router Agent -> Classify query
    2. Retrieval Agent -> Search records
    3. Context Builder Agent -> Organize results
    4. Citation Agent -> Extract evidence
    5. Answer Agent -> Generate response
    """
    
    def __init__(self):
        """Initialize all agents and build the graph"""
        # Initialize agents
        self.router_agent = RouterAgent()
        self.retrieval_agent = RetrievalAgent()
        self.context_builder_agent = ContextBuilderAgent()
        self.citation_agent = CitationAgent()
        self.answer_agent = AnswerAgent()
        
        # Build the workflow graph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes (one for each agent)
        workflow.add_node("router", self._run_router)
        workflow.add_node("retriever", self._run_retriever)
        workflow.add_node("context_builder", self._run_context_builder)
        workflow.add_node("citation", self._run_citation)
        workflow.add_node("answer", self._run_answer)
        
        # Define the flow
        workflow.set_entry_point("router")
        workflow.add_edge("router", "retriever")
        workflow.add_edge("retriever", "context_builder")
        workflow.add_edge("context_builder", "citation")
        workflow.add_edge("citation", "answer")
        workflow.add_edge("answer", END)
        
        return workflow.compile()
    
    def _run_router(self, state: AgentState) -> AgentState:
        """Execute router agent"""
        print("🔀 Router Agent: Classifying query...")
        
        result = self.router_agent.route(state['question'])
        
        state['router_result'] = result
        state['agents_used'].append("router")
        
        print(f"   Category: {result['category']}")
        return state
    
    def _run_retriever(self, state: AgentState) -> AgentState:
        """Execute retrieval agent"""
        print("🔍 Retrieval Agent: Searching records...")
        
        retrieval_start = time.time()
        
        records = self.retrieval_agent.retrieve(
            question=state['question'],
            patient_id=state.get('patient_id'),
            top_k=state.get('max_sources', 5)
        )
        
        retrieval_time = int((time.time() - retrieval_start) * 1000)
        
        state['retrieved_records'] = records
        state['retrieval_time_ms'] = retrieval_time
        state['agents_used'].append("retriever")
        
        print(f"   Found {len(records)} relevant records ({retrieval_time}ms)")
        return state
    
    def _run_context_builder(self, state: AgentState) -> AgentState:
        """Execute context builder agent"""
        print("🧩 Context Builder Agent: Organizing records...")
        
        context = self.context_builder_agent.build_context(
            question=state['question'],
            retrieved_records=state['retrieved_records'],
            category=state['router_result']['category']
        )
        
        state['context'] = context
        state['agents_used'].append("context_builder")
        
        print(f"   Built context with {context['total_records']} records")
        return state
    
    def _run_citation(self, state: AgentState) -> AgentState:
        """Execute citation agent"""
        print("📝 Citation Agent: Extracting evidence...")
        
        citations = self.citation_agent.create_citations(
            question=state['question'],
            context=state['context']
        )
        
        state['citations'] = citations
        state['agents_used'].append("citation")
        
        print(f"   Created {len(citations)} citations")
        return state
    
    def _run_answer(self, state: AgentState) -> AgentState:
        """Execute answer agent"""
        print("💬 Answer Agent: Generating response...")
        
        answer = self.answer_agent.generate_answer(
            question=state['question'],
            context=state['context'],
            citations=state['citations'],
            category=state['router_result']['category']
        )
        
        state['final_answer'] = answer
        state['agents_used'].append("answer")
        
        # Calculate total time
        state['total_time_ms'] = int((time.time() - state['start_time']) * 1000)
        
        print(f"   Answer generated ({state['total_time_ms']}ms total)")
        return state
    
    def query(
        self,
        question: str,
        patient_id: str = None,
        max_sources: int = 5
    ) -> Dict:
        """
        Execute the full workflow for a query
        
        Args:
            question: The question to answer
            patient_id: Optional patient ID filter
            max_sources: Maximum number of sources to retrieve
            
        Returns:
            Dictionary with answer, citations, and trace
        """
        print("\n" + "=" * 60)
        print("MEDGRAPH AI - QUERY PROCESSING")
        print("=" * 60)
        print(f"Question: {question}")
        if patient_id:
            print(f"Patient Filter: {patient_id}")
        print()
        
        # Initialize state
        initial_state = {
            "question": question,
            "patient_id": patient_id,
            "max_sources": max_sources,
            "agents_used": [],
            "start_time": time.time()
        }
        
        # Run the workflow
        final_state = self.graph.invoke(initial_state)
        
        # Format the response
        response = {
            "answer": final_state['final_answer'],
            "citations": final_state['citations'],
            "agent_trace": {
                "router_decision": final_state['router_result']['category'],
                "agents_used": final_state['agents_used'],
                "retrieval_time_ms": final_state['retrieval_time_ms'],
                "total_time_ms": final_state['total_time_ms']
            }
        }
        
        print("\n" + "=" * 60)
        print("✅ QUERY COMPLETE")
        print("=" * 60)
        
        return response

# Test the workflow
if __name__ == "__main__":
    workflow = MedicalRecordsWorkflow()
    
    # Test query
    result = workflow.query(
        question="What medications is John Doe taking?",
        patient_id="P001"
    )
    
    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nCitations: {len(result['citations'])}")
    print(f"Processing Time: {result['agent_trace']['total_time_ms']}ms")