"""GPT-powered summary and local rule-based resolution assistant."""

import os
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class ResolutionAgent:
    """Summarize with GPT when configured; always recommend resolution locally."""

    RESOLUTIONS = {
        "Delivery": "Check the order tracking details and contact the delivery partner if the shipment is delayed.",
        "Product Quality": "Review the complaint and verify the product damage details before initiating the marketplace return process.",
        "Payment": "Verify the payment transaction and check whether a duplicate charge was recorded.",
        "Refund": "Check the refund status and verify the original payment transaction.",
        "Other": "Review the complaint and forward it to the appropriate marketplace support team.",
    }
    SYSTEM_INSTRUCTION = "Summarize this marketplace complaint in one factual sentence of at most 20 words. Do not invent facts, order details, or promises."

    def __init__(self, client=None, api_key=None, model=None):
        self.api_key = os.getenv("OPENAI_API_KEY", "") if api_key is None else api_key
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = client

    @staticmethod
    def local_summary(complaint_text: str) -> str:
        """Return a short extractive summary based on the first sentence."""
        clean = re.sub(r"\s+", " ", (complaint_text or "")).strip()
        if not clean:
            return "No complaint text was provided."
        first_sentence = re.split(r"(?<=[.!?])\s+", clean, maxsplit=1)[0]
        words = first_sentence.split()
        return " ".join(words[:20]) + ("…" if len(words) > 20 else "")

    def recommend_resolution(self, category: str) -> str:
        return self.RESOLUTIONS.get(category, self.RESOLUTIONS["Other"])

    def resolve(self, complaint_text: str, category: str, priority: str) -> dict:
        # Only complaint text and category are sent as user data to the API.
        summary_method = "GPT"
        status = "GPT summarization used."
        summary = ""
        if not self.api_key:
            summary = self.local_summary(complaint_text)
            summary_method = "Local fallback"
            status = "Local summary used — API key not configured."
        else:
            try:
                client = self.client or OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_INSTRUCTION},
                        {"role": "user", "content": f"Category: {category}\nComplaint: {complaint_text}"},
                    ],
                    max_tokens=60,
                    temperature=0.2,
                )
                summary = response.choices[0].message.content.strip()
                if not summary:
                    raise ValueError("The summary response was empty.")
            except Exception:
                summary = self.local_summary(complaint_text)
                summary_method = "Local fallback"
                status = "Local summary used — GPT request failed."
        return {
            "summary": summary,
            "resolution": self.recommend_resolution(category),
            "summarization_method": summary_method,
            "status": status,
        }

    def run(self, complaint_text: str, category: str, priority: str) -> dict:
        return self.resolve(complaint_text, category, priority)
