"""Rule based complaint classification agent."""


class ClassificationAgent:
    """Classify complaint text with transparent keyword rules."""

    KEYWORDS = {
        "Delivery": ("delivery", "delivered", "shipment", "shipping", "order late", "late order", "package", "tracking"),
        "Product Quality": ("damaged", "broken", "defective", "quality", "faulty", "wrong item", "not working"),
        "Payment": ("charged twice", "duplicate payment", "duplicate charge", "payment", "charged", "billing", "transaction"),
        "Refund": ("refund", "money back", "reimbursement", "repaid"),
    }

    def classify(self, complaint_text: str) -> dict:
        text = (complaint_text or "").lower()
        for category, keywords in self.KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return {"category": category, "reason": f"Matched a {category.lower()} keyword in the complaint."}
        return {"category": "Other", "reason": "No delivery, product quality, payment, or refund keyword matched."}

    def run(self, complaint_text: str) -> dict:
        return self.classify(complaint_text)
