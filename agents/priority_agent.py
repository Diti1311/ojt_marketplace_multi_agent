"""Transparent complaint priority rules."""


class PriorityAgent:
    """Assign High, Medium, or Low priority using simple rules."""

    HIGH_TERMS = ("damaged", "broken", "defective", "charged twice", "duplicate charge", "duplicate payment", "fraud", "unauthorized")

    def assess(self, complaint_text: str, category: str) -> dict:
        text = (complaint_text or "").lower()
        if any(term in text for term in self.HIGH_TERMS):
            return {"priority": "High", "reason": "Damage, duplicate charge, or another urgent issue was reported."}
        if category in ("Delivery", "Refund", "Payment"):
            return {"priority": "Medium", "reason": f"The {category.lower()} issue needs follow-up but no urgent risk keyword was found."}
        return {"priority": "Low", "reason": "General inquiry or non-urgent issue with no high-priority keyword."}

    def run(self, complaint_text: str, category: str) -> dict:
        return self.assess(complaint_text, category)
