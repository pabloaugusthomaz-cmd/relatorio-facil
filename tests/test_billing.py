import unittest
import json
from decimal import Decimal
from unittest.mock import Mock, patch

from billing import approved_payment, compare_report, create_checkout


class BillingTests(unittest.TestCase):
    def test_checkout_uses_fixed_product_amount_and_external_reference(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = json.dumps({"init_point": "https://pay.example/checkout"}).encode()

        with patch("billing.urlopen", return_value=response) as mocked_urlopen:
            url = create_checkout("secret", "order-123", "https://app.example")

        self.assertEqual(url, "https://pay.example/checkout")
        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.mercadopago.com/checkout/preferences")
        self.assertEqual(request.headers["Authorization"], "Bearer secret")
        payload = json.loads(request.data)
        self.assertEqual(payload["external_reference"], "order-123")
        self.assertEqual(payload["items"][0]["unit_price"], 19.9)
        self.assertEqual(payload["back_urls"]["success"], "https://app.example")

    def test_only_live_approved_matching_payment_unlocks(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = json.dumps({
            "status": "approved",
            "live_mode": True,
            "external_reference": "order-123",
            "currency_id": "BRL",
            "transaction_amount": 19.9,
        }).encode()

        with patch("billing.urlopen", return_value=response):
            self.assertTrue(approved_payment("secret", "456", "order-123"))
        response.read.return_value = json.dumps({
            "status": "approved", "live_mode": True, "external_reference": "order-123",
            "currency_id": "BRL", "transaction_amount": 1.0,
        }).encode()
        with patch("billing.urlopen", return_value=response):
            self.assertFalse(approved_payment("secret", "456", "order-123"))
            self.assertFalse(approved_payment("secret", "not-an-id", "order-123"))

    def test_comparative_report_escapes_product_names_and_shows_difference(self):
        first = {"name": "old.csv", "totals": {"<script>": Decimal("100.00")}}
        second = {"name": "new.csv", "totals": {"<script>": Decimal("125.00"), "B": Decimal("10")}}

        report = compare_report(first, second)

        self.assertIn("&lt;script&gt;", report)
        self.assertNotIn("<script>", report)
        self.assertIn("R$ 35,00 (+35.0%)", report)
        self.assertIn("new.csv", report)


if __name__ == "__main__":
    unittest.main()
