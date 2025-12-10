"""Modelo base de Utilizador."""
from dataclasses import dataclass

@dataclass
class User:
    """Classe base para Admin e Vendedor."""
    username: str
    email: str
    password: str  # texto simples para projeto académico
    role: str      # "ADMIN" ou "VENDOR"

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "role": self.role,
        }
