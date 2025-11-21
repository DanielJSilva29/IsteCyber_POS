from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QMessageBox,
    QLabel, QFrame
)
from PyQt5.QtCore import pyqtSignal, Qt
import random, string

class RecoverPasswordPage(QWidget):
    """Página de recuperação de password, em 3 passos (sem APIs externas)."""
    back = pyqtSignal()

    def __init__(self, system_manager):
        super().__init__()
        self.sm = system_manager
        self.code = None
        self.target_user = None
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)

        card = QFrame()
        card.setObjectName("recoverCard")
        card.setStyleSheet(
            "#recoverCard {"
            "  background-color: #2a2a2a;"
            "  border-radius: 12px;"
            "  border: 1px solid #444;"
            "  padding: 20px;"
            "}"
        )
        v = QVBoxLayout(card)

        title = QLabel("Recuperar Password")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        desc = QLabel("Simulação de fluxo de recuperação de password sem envio real de email.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #aaa;")

        step1_label = QLabel("Passo 1 — Introduza o email da conta:")
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email registado")
        self.btn_send = QPushButton("Gerar código de recuperação")

        self.simulated_email = QLabel("Área de simulação de email: nenhum código gerado ainda.")
        self.simulated_email.setWordWrap(True)
        self.simulated_email.setStyleSheet(
            "background-color: #111; border: 1px solid #555; padding: 8px; font-family: monospace;"
        )

        step3_label = QLabel("Passo 2 — Introduza o código e a nova password:")
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Código de 6 dígitos")
        self.new_pwd = QLineEdit()
        self.new_pwd.setPlaceholderText("Nova password")
        self.new_pwd.setEchoMode(QLineEdit.Password)

        self.btn_toggle = QPushButton("👁")
        self.btn_toggle.setCheckable(True)
        self.btn_toggle.setFixedWidth(32)
        self.btn_toggle.toggled.connect(self._toggle_pwd)

        pwd_row = QVBoxLayout()
        pwd_inner = QHBoxLayout()
        pwd_inner.addWidget(self.new_pwd)
        pwd_inner.addWidget(self.btn_toggle)
        pwd_row.addLayout(pwd_inner)

        self.btn_reset = QPushButton("Redefinir Password")
        btn_back = QPushButton("Voltar")

        v.addWidget(title)
        v.addWidget(desc)
        v.addSpacing(8)
        v.addWidget(step1_label)
        v.addWidget(self.email)
        v.addWidget(self.btn_send)
        v.addSpacing(8)
        v.addWidget(QLabel("Simulação de email recebido:"))
        v.addWidget(self.simulated_email)
        v.addSpacing(8)
        v.addWidget(step3_label)
        v.addWidget(self.code_input)
        v.addLayout(pwd_row)
        v.addWidget(self.btn_reset)
        v.addSpacing(10)
        v.addWidget(btn_back, alignment=Qt.AlignRight)

        root.addWidget(card)

        self.btn_send.clicked.connect(self._send_code)
        self.btn_reset.clicked.connect(self._reset)
        btn_back.clicked.connect(self.back.emit)

    def _toggle_pwd(self, checked: bool):
        self.new_pwd.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)

    def _send_code(self):
        email = self.email.text().strip()
        if not email:
            self.email.setStyleSheet("border: 1px solid red;")
            return
        self.email.setStyleSheet("")

        self.target_user = None
        for u in self.sm.list_users():
            if u["email"].lower() == email.lower():
                self.target_user = u
                break
        if not self.target_user:
            QMessageBox.critical(self, "Erro", "Email não registado.")
            return

        self.code = "".join(random.choices(string.digits, k=6))
        self.simulated_email.setText(
            f"De: no-reply@sistemapos.local\n"
            f"Para: {email}\n"
            f"Assunto: Código de recuperação\n\n"
            f"O seu código de recuperação é: {self.code}\n"
            f"(Nota: isto é uma simulação, não é enviado nenhum email real.)"
        )
        QMessageBox.information(self, "Código gerado", "Código gerado e 'enviado' para a área de simulação.")

    def _reset(self):
        if not (self.target_user and self.code):
            QMessageBox.warning(self, "Aviso", "Gere primeiro um código de recuperação.")
            return
        if self.code_input.text().strip() != self.code:
            QMessageBox.critical(self, "Erro", "Código inválido.")
            return
        if not self.new_pwd.text().strip():
            QMessageBox.warning(self, "Aviso", "Introduza a nova password.")
            return

        users = self.sm._load_json(self.sm.USERS)
        for u in users:
            if u["username"] == self.target_user["username"]:
                u["password"] = self.new_pwd.text()
                break
        self.sm._save_json(self.sm.USERS, users)
        QMessageBox.information(self, "OK", "Password redefinida com sucesso.")

        self.code = None
        self.target_user = None
        self.email.clear()
        self.code_input.clear()
        self.new_pwd.clear()
        self.simulated_email.setText("Área de simulação de email: nenhum código gerado ainda.")