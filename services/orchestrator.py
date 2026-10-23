"""Sequential complaint processing orchestrator."""

from uuid import uuid4

from agents.classification_agent import ClassificationAgent
from agents.priority_agent import PriorityAgent
from agents.resolution_agent import ResolutionAgent


class ComplaintOrchestrator:
    """Run classification, priority, and resolution agents in order."""

    def __init__(self, classification_agent=None, priority_agent=None, resolution_agent=None):
        self.classification_agent = classification_agent or ClassificationAgent()
        self.priority_agent = priority_agent or PriorityAgent()
        self.resolution_agent = resolution_agent or ResolutionAgent()

    def process(self, complaint_text: str, customer_name: str = "", order_id: str = "") -> dict:
        classification = self.classification_agent.run(complaint_text)
        priority = self.priority_agent.run(complaint_text, classification["category"])
        resolution = self.resolution_agent.run(complaint_text, classification["category"], priority["priority"])
        return {
            "complaint_id": f"CMP-{uuid4().hex[:8].upper()}",
            "complaint_text": complaint_text,
            "category": classification["category"],
            "classification_reason": classification["reason"],
            "priority": priority["priority"],
            "priority_reason": priority["reason"],
            "summary": resolution["summary"],
            "resolution": resolution["resolution"],
            "summarization_method": resolution["summarization_method"],
            "status": resolution["status"],
        }
