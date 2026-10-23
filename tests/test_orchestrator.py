"""Tests for the sequential complaint orchestrator."""

from agents.classification_agent import ClassificationAgent
from agents.priority_agent import PriorityAgent
from agents.resolution_agent import ResolutionAgent
from services.orchestrator import ComplaintOrchestrator


def test_agents_run_in_order_and_outputs_are_passed_between_them():
    calls = []

    class Classifier:
        def run(self, complaint_text):
            calls.append(("classification", complaint_text))
            return {"category": "Delivery", "reason": "delivery keyword"}

    class Prioritizer:
        def run(self, complaint_text, category):
            calls.append(("priority", complaint_text, category))
            return {"priority": "Medium", "reason": "follow-up"}

    class Resolver:
        def run(self, complaint_text, category, priority):
            calls.append(("resolution", complaint_text, category, priority))
            return {"summary": "Late delivery.", "resolution": "Check tracking.", "summarization_method": "Local fallback", "status": "Local summary used."}

    result = ComplaintOrchestrator(Classifier(), Prioritizer(), Resolver()).process("My order is late")
    assert [call[0] for call in calls] == ["classification", "priority", "resolution"]
    assert calls[1] == ("priority", "My order is late", "Delivery")
    assert calls[2] == ("resolution", "My order is late", "Delivery", "Medium")
    assert result["complaint_id"].startswith("CMP-")
    assert result == {
        "complaint_id": result["complaint_id"], "complaint_text": "My order is late",
        "category": "Delivery", "classification_reason": "delivery keyword",
        "priority": "Medium", "priority_reason": "follow-up", "summary": "Late delivery.",
        "resolution": "Check tracking.", "summarization_method": "Local fallback", "status": "Local summary used.",
    }


def test_real_agents_return_complete_result_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = ComplaintOrchestrator(ClassificationAgent(), PriorityAgent(), ResolutionAgent(api_key="")).process(
        "My order was delivered late."
    )
    assert set(result) == {
        "complaint_id", "complaint_text", "category", "classification_reason", "priority",
        "priority_reason", "summary", "resolution", "summarization_method", "status",
    }
    assert result["category"] == "Delivery"
    assert result["priority"] == "Medium"
    assert result["summarization_method"] == "Local fallback"
