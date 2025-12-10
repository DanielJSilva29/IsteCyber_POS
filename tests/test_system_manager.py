import unittest
import tempfile
from pathlib import Path

from models.system_manager import SystemManager
from models.product import Product

class TestSystemManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name) / "data"
        base.mkdir()
        (base / "users.json").write_text("[]", encoding="utf-8")
        (base / "products.json").write_text("[]", encoding="utf-8")
        (base / "sales.json").write_text("[]", encoding="utf-8")

        SystemManager.USERS = base / "users.json"
        SystemManager.PRODUCTS = base / "products.json"
        SystemManager.SALES = base / "sales.json"
        self.sm = SystemManager()

    def tearDown(self):
        self.tmp.cleanup()

    def test_register_and_login_admin(self):
        self.sm.register_admin(company="ISTEC", vat="505", shop_type="RESTAURACAO",
                               username="admin1", email="admin1@email", password="123")
        user = self.sm.login("admin1", "123")
        self.assertIsNotNone(user)
        self.assertEqual(user["role"], "ADMIN")

    def test_add_product(self):
        p = Product(code="C01", name="Coca-Cola", price_no_vat=1.0, ptype="Drinks")
        saved = self.sm.add_product(p)
        self.assertEqual(saved["code"], "C01")

    def test_create_invoice(self):
        self.sm.add_product(Product(code="C01", name="Coca-Cola", price_no_vat=1.0, ptype="Drinks"))
        invoice = self.sm.create_invoice(
            items=[{"code": "C01", "name": "Coca-Cola", "qty": 2, "price_no_vat": 1.0}],
            seller_username="v1",
        )
        self.assertAlmostEqual(invoice["total_with_vat"], 2.46, places=2)

if __name__ == "__main__":
    unittest.main()
