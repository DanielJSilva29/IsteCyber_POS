import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from models.system_manager import SystemManager
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.management_page import ManagementPage
from pages.sales_page import SalesPage
from pages.recover_password_page import RecoverPasswordPage
from pages.inventory_page import InventoryPage
from pages.profile_page import ProfilePage
from pages.dashboard_page import DashboardPage

class MainArea(QWidget):
    """Zona principal após login, com navegação no topo."""
    def __init__(self, system_manager, current_user: dict, on_logout):
        super().__init__()
        self.sm = system_manager
        self.user = current_user
        self.on_logout = on_logout
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        topbar = QHBoxLayout()
        self.btn_manage = QPushButton("Gestão")
        self.btn_sales = QPushButton("Vendas")
        self.btn_inventory = QPushButton("Inventário")
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_profile = QPushButton("Perfil")
        self.btn_logout = QPushButton("Logout")

        for b in (self.btn_manage, self.btn_sales, self.btn_inventory,
                  self.btn_dashboard, self.btn_profile, self.btn_logout):
            b.setCursor(Qt.PointingHandCursor)

        topbar.addWidget(self.btn_manage)
        topbar.addWidget(self.btn_sales)
        topbar.addWidget(self.btn_inventory)
        topbar.addWidget(self.btn_dashboard)
        topbar.addWidget(self.btn_profile)
        topbar.addStretch()
        topbar.addWidget(self.btn_logout)

        layout.addLayout(topbar)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        # --- CRIAÇÃO DAS PÁGINAS ---
        # Passamos self.user para todas as páginas que precisam de saber quem está logado
        
        self.page_manage = ManagementPage(self.sm, self.user) if self.user.get("role") == "ADMIN" else None
        self.page_sales = SalesPage(self.sm, self.user)
        self.page_inventory = InventoryPage(self.sm, self.user) if self.user.get("role") == "ADMIN" else None
        
        # CORREÇÃO AQUI: Adicionado self.user ao DashboardPage
        self.page_dashboard = DashboardPage(self.sm, self.user) if self.user.get("role") == "ADMIN" else None
        
        self.page_profile = ProfilePage(self.sm, self.user, self.on_logout)

        if self.page_manage:
            self.stack.addWidget(self.page_manage)
        self.stack.addWidget(self.page_sales)
        if self.page_inventory:
            self.stack.addWidget(self.page_inventory)
        if self.page_dashboard:
            self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_profile)

        # --- Lógica de Índices para Navegação ---
        idx = 0
        self.idx_manage = idx if self.page_manage else None
        if self.page_manage:
            idx += 1
        self.idx_sales = idx
        idx += 1
        self.idx_inventory = idx if self.page_inventory else None
        if self.page_inventory:
            idx += 1
        self.idx_dashboard = idx if self.page_dashboard else None
        if self.page_dashboard:
            idx += 1
        self.idx_profile = idx

        # Ligações de navegação interna (ex: botão na gestão que leva às vendas)
        if self.page_manage:
            self.page_manage.goto_sales.connect(lambda: self.stack.setCurrentIndex(self.idx_sales))
            self.page_manage.goto_stats.connect(lambda: self.stack.setCurrentIndex(self.idx_dashboard))
        
        if self.page_sales:
             self.page_sales.back_to_manage.connect(lambda: self.stack.setCurrentIndex(self.idx_manage) if self.idx_manage is not None else None)

        # Ligações dos botões do menu superior
        self.btn_manage.clicked.connect(lambda: self.stack.setCurrentIndex(self.idx_manage) if self.idx_manage is not None else None)
        self.btn_sales.clicked.connect(lambda: self.stack.setCurrentIndex(self.idx_sales))
        self.btn_inventory.clicked.connect(lambda: self.stack.setCurrentIndex(self.idx_inventory) if self.idx_inventory is not None else None)
        self.btn_dashboard.clicked.connect(lambda: self.stack.setCurrentIndex(self.idx_dashboard) if self.idx_dashboard is not None else None)
        self.btn_profile.clicked.connect(lambda: self.stack.setCurrentIndex(self.idx_profile))
        self.btn_logout.clicked.connect(self.on_logout)

        # Esconder botões de Admin para Vendedores
        if self.user.get("role") != "ADMIN":
            self.btn_manage.hide()
            self.btn_inventory.hide()
            self.btn_dashboard.hide()
            self.stack.setCurrentIndex(self.idx_sales)
        else:
            self.btn_manage.show()
            self.btn_inventory.show()
            self.btn_dashboard.show()
            # Admin começa na gestão (ou vendas se gestão falhar)
            self.stack.setCurrentIndex(self.idx_manage if self.idx_manage is not None else self.idx_sales)


class POSMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sm = SystemManager()
        self.current_user = None
        self.central = QStackedWidget()
        self.setCentralWidget(self.central)

        self.login = LoginPage(self.sm)
        self.register = RegisterPage(self.sm, on_back=lambda: self.central.setCurrentWidget(self.login))
        self.recover = RecoverPasswordPage(self.sm)
        self.main_area = None

        self.central.addWidget(self.login)
        self.central.addWidget(self.register)
        self.central.addWidget(self.recover)
        self.central.setCurrentWidget(self.login)

        self.login.goto_register.connect(lambda: self.central.setCurrentWidget(self.register))
        self.login.goto_recover.connect(lambda: self.central.setCurrentWidget(self.recover))
        self.login.login_success.connect(self._on_login_success)
        self.recover.back.connect(lambda: self.central.setCurrentWidget(self.login))

        self._apply_theme_accent("#ff5555")

    def _apply_theme_accent(self, color_hex: str):
        style_path = Path(__file__).resolve().parent / "style" / "style.qss"
        base_style = style_path.read_text(encoding="utf-8") if style_path.exists() else ""
        extra = f"""
QPushButton {{
    background-color: {color_hex};
    border-radius: 6px;
    padding: 6px 10px;
}}
QPushButton:hover {{
    background-color: {color_hex};
}}
"""
        self.setStyleSheet(base_style + "\n" + extra)

    def _on_login_success(self, user: dict):
        self.current_user = user
        shop_type = user.get("shop_type", "OUTRO")
        # Cores temáticas por loja
        accents = {
            "RESTAURACAO": "#e53935",
            "FARMACIA": "#43a047",
            "OFICINA": "#fdd835",
            "OUTRO": "#fb8c00",
        }
        self._apply_theme_accent(accents.get(shop_type, "#ff5555"))

        # Cria a área principal passando o utilizador logado
        self.main_area = MainArea(self.sm, user, on_logout=self._logout)
        if self.central.indexOf(self.main_area) == -1:
            self.central.addWidget(self.main_area)
        self.central.setCurrentWidget(self.main_area)

    def _logout(self):
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Terminar sessão", "Deseja terminar sessão?")
        if reply != QMessageBox.Yes:
            return
        
        # Remove a área principal antiga para recriar no próximo login
        if self.main_area:
            self.central.removeWidget(self.main_area)
            self.main_area.deleteLater()
            self.main_area = None
            
        self.current_user = None
        self.central.setCurrentWidget(self.login)


def main():
    app = QApplication(sys.argv)
    w = POSMainWindow()
    w.setWindowTitle("Sistema POS (PyQt5)")
    icon_path = Path(__file__).resolve().parent / "icons" / "product.png"
    if icon_path.exists():
        w.setWindowIcon(QIcon(str(icon_path)))
    w.resize(1100, 700)
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()