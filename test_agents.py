"""Offline unit tests for the synthetic marketplace agents."""

import unittest

from agents import (
    InventoryAgent,
    MarketplaceResponseAgent,
    ProductDataAgent,
    run_workflow,
)


class MarketplaceAgentTests(unittest.TestCase):
    def setUp(self):
        self.pharmacy_products = ProductDataAgent().run("Pharmacy")["output"]

    def test_product_data_agent_returns_three_pharmacy_products(self):
        self.assertEqual(len(self.pharmacy_products), 3)
        self.assertTrue(all(product["category"] == "Pharmacy" for product in self.pharmacy_products))

    def test_inventory_agent_marks_positive_stock_available(self):
        result = InventoryAgent().run(self.pharmacy_products)
        for product in result["output"]:
            if product["stock"] > 0:
                self.assertEqual(product["availability"], "Available")

    def test_inventory_agent_marks_zero_stock_out_of_stock(self):
        result = InventoryAgent().run(self.pharmacy_products)
        zero_stock_products = [product for product in result["output"] if product["stock"] == 0]
        self.assertTrue(zero_stock_products)
        self.assertTrue(all(product["availability"] == "Out of Stock" for product in zero_stock_products))

    def test_response_agent_excludes_out_of_stock_products(self):
        checked_products = InventoryAgent().run(self.pharmacy_products)["output"]
        result = MarketplaceResponseAgent().run(checked_products, 1000)
        self.assertTrue(all(product["availability"] == "Available" for product in result["output"]))
        self.assertNotIn("P003", [product["product_id"] for product in result["output"]])

    def test_response_agent_excludes_products_above_maximum_price(self):
        checked_products = InventoryAgent().run(self.pharmacy_products)["output"]
        result = MarketplaceResponseAgent().run(checked_products, 300)
        self.assertTrue(all(product["price"] <= 300 for product in result["output"]))
        self.assertNotIn("P002", [product["product_id"] for product in result["output"]])

    def test_pharmacy_workflow_at_500_returns_p001_and_p002(self):
        result = run_workflow("Pharmacy", 500)
        self.assertEqual(
            {product["product_id"] for product in result["final_matching_products"]},
            {"P001", "P002"},
        )

    def test_trace_has_three_agents_in_order(self):
        result = run_workflow("Pharmacy", 500)
        self.assertEqual(
            [entry["agent_name"] for entry in result["agent_execution_trace"]],
            ["ProductDataAgent", "InventoryAgent", "MarketplaceResponseAgent"],
        )

    def test_each_agent_output_is_next_agent_input(self):
        result = run_workflow("Pharmacy", 500)
        trace = result["agent_execution_trace"]
        self.assertEqual(trace[0]["output"], trace[1]["input"])
        self.assertEqual(trace[1]["output"], trace[2]["input"]["products"])


if __name__ == "__main__":
    unittest.main()
