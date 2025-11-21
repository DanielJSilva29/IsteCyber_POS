from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QMessageBox, QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import pyqtSignal, Qt

class LoginPage(QWidget):
    """Página de Login para Admin e Vendedor."""
    login_success = pyqtSignal(dict)
    goto_register = pyqtSignal()
    goto_recover = pyqtSignal()

    def __init__(self, system_manager):
        super().__init__()
        self.sm = system_manager
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)

        root.addItem(QSpacerItem(40, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))

        card = QFrame()
        card.setObjectName("loginCard")
        card.setStyleSheet(
            "#loginCard {"
            "  background-color: #2a2a2a;"
            "  border-radius: 12px;"
            "  padding: 24px;"
            "  border: 1px solid #444;"
            "}"
        )
        v = QVBoxLayout(card)
        v.setSpacing(10)

        title = QLabel("Sistema POS")
        subtitle = QLabel("Login de Administrador / Vendedor")
        title.setAlignment(Qt.AlignCenter)
        subtitle.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        subtitle.setStyleSheet("color: #aaa;")

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")
        self.pwd = QLineEdit()
        self.pwd.setPlaceholderText("Password")
        self.pwd.setEchoMode(QLineEdit.Password)

        pwd_row = QHBoxLayout()
        pwd_row.addWidget(self.pwd)
        self.btn_toggle = QPushButton("👁")
        self.btn_toggle.setCheckable(True)
        self.btn_toggle.setFixedWidth(32)
        self.btn_toggle.toggled.connect(self._toggle_pwd)
        pwd_row.addWidget(self.btn_toggle)

        btn_login = QPushButton("Entrar")
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.setDefault(True)

        links_row = QHBoxLayout()
        link_register = QPushButton("Criar conta (Admin)")
        link_register.setFlat(True)
        link_register.setCursor(Qt.PointingHandCursor)
        link_recover = QPushButton("Recuperar Password")
        link_recover.setFlat(True)
        link_recover.setCursor(Qt.PointingHandCursor)
        links_row.addWidget(link_register)
        links_row.addStretch()
        links_row.addWidget(link_recover)

        v.addWidget(title)
        v.addWidget(subtitle)
        v.addSpacing(10)
        v.addWidget(self.user)
        v.addLayout(pwd_row)
        v.addSpacing(8)
        v.addWidget(btn_login)
        v.addSpacing(6)
        v.addLayout(links_row)

        root.addWidget(card)
        root.addItem(QSpacerItem(40, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))

        btn_login.clicked.connect(self._on_login)
        link_register.clicked.connect(self.goto_register.emit)
        link_recover.clicked.connect(self.goto_recover.emit)

    def _toggle_pwd(self, checked: bool):
        self.pwd.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)

    def _on_login(self):
        username = self.user.text().strip()
        password = self.pwd.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Aviso", "Preencha username e password.")
            return
        user = self.sm.login(username, password)
        if user:
            self.login_success.emit(user)
        else:
            QMessageBox.critical(self, "Erro", "Credenciais inválidas.")
