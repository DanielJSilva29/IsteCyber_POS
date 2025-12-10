"""Modelo de Vendedor."""
from .user import User

class Vendor(User):
    """Vendedor da loja."""
    def __init__(self, username: str, email: str, password: str):
        super().__init__(username=username, email=email, password=password, role="VENDOR")
