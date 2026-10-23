"""Beginner-friendly tests for the three complaint agents."""

from unittest.mock import Mock

from agents.classification_agent import ClassificationAgent
from agents.priority_agent import PriorityAgent
from agents.resolution_agent import ResolutionAgent


def test_classifies_delivery():
    assert ClassificationAgent().classify("My order was delivered late.")["category"] == "Delivery"


def test_classifies_damaged_product():
    assert ClassificationAgent().classify("I received a damaged product.")["category"] == "Product Quality"


def test_classifies_duplicate_payment():
    assert ClassificationAgent().classify("I was charged twice for the same order.")["category"] == "Payment"


def test_classifies_refund():
    assert ClassificationAgent().classify("My refund has not arrived.")["category"] == "Refund"


def test_high_priority_for_damage():
    assert PriorityAgent().assess("The item is damaged", "Product Quality")["priority"] == "High"


def test_medium_priority_for_late_delivery():
    assert PriorityAgent().assess("My order is late", "Delivery")["priority"] == "Medium"


def test_low_priority_for_general_question():
    assert PriorityAgent().assess("What are your store hours?", "Other")["priority"] == "Low"


def test_resolution_for_every_category():
    agent = ResolutionAgent(api_key="")
    for category in ("Delivery", "Product Quality", "Payment", "Refund", "Other"):
        assert agent.recommend_resolution(category)
    assert "tracking" in agent.recommend_resolution("Delivery")
    assert "damage" in agent.recommend_resolution("Product Quality")
    assert "transaction" in agent.recommend_resolution("Payment")
    assert "refund status" in agent.recommend_resolution("Refund")
    assert "support team" in agent.recommend_resolution("Other")


def test_local_summarizer_without_api_key():
    result = ResolutionAgent(api_key="").resolve("My order arrived late. Please help.", "Delivery", "Medium")
    assert result["summary"] == "My order arrived late."
    assert result["summarization_method"] == "Local fallback"
    assert "API key not configured" in result["status"]


def test_api_is_called_with_configured_key_and_only_summary_content():
    message = Mock(content="Customer reports late delivery.")
    choice = Mock(message=message)
    response = Mock(choices=[choice])
    client = Mock()
    client.chat.completions.create.return_value = response
    secret = "sk-test-secret-do-not-return"
    result = ResolutionAgent(client=client, api_key=secret, model="gpt-4o-mini").resolve(
        "My order was delivered late.", "Delivery", "Medium"
    )
    client.chat.completions.create.assert_called_once()
    kwargs = client.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == "gpt-4o-mini"
    assert kwargs["max_tokens"] <= 60
    assert kwargs["messages"][0]["role"] == "system"
    assert "My order was delivered late." in kwargs["messages"][1]["content"]
    assert "Delivery" in kwargs["messages"][1]["content"]
    assert result["summary"] == "Customer reports late delivery."
    assert secret not in repr(result)


def test_fallback_when_api_raises_and_key_is_not_exposed():
    client = Mock()
    client.chat.completions.create.side_effect = RuntimeError("failure, sk-test-secret")
    secret = "sk-test-secret"
    result = ResolutionAgent(client=client, api_key=secret).resolve("Product is broken.", "Product Quality", "High")
    assert result["summarization_method"] == "Local fallback"
    assert "GPT request failed" in result["status"]
    assert secret not in repr(result)


def test_empty_key_does_not_call_client():
    client = Mock()
    result = ResolutionAgent(client=client, api_key="").resolve("It is late", "Delivery", "Medium")
    client.chat.completions.create.assert_not_called()
    assert result["summarization_method"] == "Local fallback"
