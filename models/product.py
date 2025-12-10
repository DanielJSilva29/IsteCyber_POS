"""Modelo de Produto."""
from dataclasses import dataclass

@dataclass
class Product:
    """Representa um produto disponível para venda."""
    code: str
    name: str
    price_no_vat: float
    ptype: str
    image_path: str = ""
    stock: int = 0
    min_stock: int = 0
    company: str = ""      # empresa / dono do produto
    shop_type: str = ""    # RESTAURACAO, OFICINA, etc.

    def to_dict(self) -> dict:
        """Converte o produto para dicionário serializável em JSON."""
        return {
            "code": self.code,
            "name": self.name,
            "price_no_vat": self.price_no_vat,
            "ptype": self.ptype,
            "image_path": self.image_path,
            "stock": self.stock,
            "min_stock": self.min_stock,
            "company": self.company,
            "shop_type": self.shop_type,
        }