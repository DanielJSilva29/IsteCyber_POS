"""Modelo de Administrador."""
from .user import User

class Admin(User):
    """Administrador da loja."""
    def __init__(self, username: str, email: str, password: str):
        super().__init__(username=username, email=email, password=password, role="ADMIN")
