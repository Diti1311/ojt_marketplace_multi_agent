"""Rule-based agents for the synthetic marketplace demonstration."""

from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4


PRODUCT_CATALOG = [
    {"product_id": "P001", "name": "Pharmacy Hand Sanitizer", "category": "Pharmacy", "price": 199, "stock": 25},
    {"product_id": "P002", "name": "Digital Thermometer", "category": "Pharmacy", "price": 399, "stock": 10},
    {"product_id": "P003", "name": "First Aid Kit", "category": "Pharmacy", "price": 699, "stock": 0},
    {"product_id": "P004", "name": "Wireless Mouse", "category": "Electronics", "price": 499, "stock": 15},
    {"product_id": "P005", "name": "Notebook", "category": "Stationery", "price": 99, "stock": 50},
]


class ProductDataAgent:
    """Find products in the local synthetic catalog for one category."""

    name = "ProductDataAgent"

    def run(self, category):
        products = [deepcopy(product) for product in PRODUCT_CATALOG if product["category"] == category]
        return {
            "agent_name": self.name,
            "input": {"category": category},
            "output": products,
            "status": "Success",
        }


class InventoryAgent:
    """Add an availability label to each product based on its stock."""

    name = "InventoryAgent"

    def run(self, products):
        checked_products = []
        for product in products:
            checked_product = deepcopy(product)
            checked_product["availability"] = "Available" if checked_product["stock"] > 0 else "Out of Stock"
            checked_products.append(checked_product)
        return {
            "agent_name": self.name,
            "input": deepcopy(products),
            "output": checked_products,
            "status": "Success",
        }


class MarketplaceResponseAgent:
    """Return available products at or below a maximum price."""

    name = "MarketplaceResponseAgent"

    def run(self, products, max_price):
        matches = [
            deepcopy(product)
            for product in products
            if product["availability"] == "Available" and product["price"] <= max_price
        ]
        return {
            "agent_name": self.name,
            "input": {"products": deepcopy(products), "max_price": max_price},
            "output": matches,
            "status": "Success",
        }


def run_workflow(category, max_price):
    """Run the three agents in sequence and return the complete execution record."""
    product_data_result = ProductDataAgent().run(category)
    inventory_result = InventoryAgent().run(product_data_result["output"])
    response_result = MarketplaceResponseAgent().run(inventory_result["output"], max_price)

    return {
        "run_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "selected_category": category,
        "maximum_price": max_price,
        "agent_execution_trace": [product_data_result, inventory_result, response_result],
        "final_matching_products": response_result["output"],
    }
