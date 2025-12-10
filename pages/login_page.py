from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QMessageBox, QFrame, QGraphicsDropShadowEffect, QProgressBar
)
from PyQt5.QtCore import pyqtSignal, Qt, QThread, QTimer
from PyQt5.QtGui import QColor, QCursor
import time

# --- WORKER THREAD (Processa o login em segundo plano) ---
class LoginWorker(QThread):
    finished = pyqtSignal(object) # Emite o user ou None

    def __init__(self, sm, username, password):
        super().__init__()
        self.sm = sm
        self.username = username
        self.password = password

    def run(self):
        # Pequeno delay artificial (0.5s) apenas para a animação ser vista
        # e dar a sensação de "processamento" suave, tipo Windows
        time.sleep(0.5)
        
        # Tenta fazer login
        user = self.sm.login(self.username, self.password)
        self.finished.emit(user)

# --- PÁGINA DE LOGIN ---
class LoginPage(QWidget):
    """Página de Login com Loading e Threading."""
    login_success = pyqtSignal(dict)
    goto_register = pyqtSignal()
    goto_recover = pyqtSignal()

    def __init__(self, system_manager):
        super().__init__()
        self.sm = system_manager
        self._build()

    def _build(self):
        # Layout principal centrado
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Card de Login
        card = QFrame()
        card.setFixedSize(400, 520) # Aumentei um pouco para caber a barra
        card.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 20px;
                border: 1px solid #333;
            }
        """)
        
        # Sombra do Card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 10)
        card.setGraphicsEffect(shadow)
        
        # Layout interno do Card
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 50, 40, 50)
        card_layout.setSpacing(20)
        
        # Título / Logo
        lbl_title = QLabel("Sistema POS")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size: 32px; font-weight: bold; color: white; border: none; background: transparent;")
        
        lbl_sub = QLabel("Bem-vindo de volta")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setStyleSheet("font-size: 14px; color: #888; margin-bottom: 20px; border: none; background: transparent;")
        
        # Inputs Estilizados
        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")
        self.user.setFixedHeight(45)
        self.user.setStyleSheet(self._input_style())
        
        self.pwd = QLineEdit()
        self.pwd.setPlaceholderText("Password")
        self.pwd.setEchoMode(QLineEdit.Password)
        self.pwd.setFixedHeight(45)
        self.pwd.setStyleSheet(self._input_style())
        
        # --- LOADING BAR (Tipo Windows) ---
        self.loading_bar = QProgressBar()
        self.loading_bar.setFixedHeight(4) # Fininha e elegante
        self.loading_bar.setTextVisible(False) # Sem texto "50%"
        self.loading_bar.setRange(0, 0) # Range 0-0 cria o efeito "infinito/loop"
        self.loading_bar.hide() # Escondida inicialmente
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #333;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 2px;
            }
        """)

        # Botão Entrar
        self.btn_login = QPushButton("ENTRAR")
        self.btn_login.setFixedHeight(50)
        self.btn_login.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-weight: bold;
                border-radius: 25px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004494;
            }
            QPushButton:disabled {
                background-color: #333;
                color: #555;
            }
        """)
        self.btn_login.clicked.connect(self._start_login_process)
        
        # Permitir Enter para login
        self.user.returnPressed.connect(self._start_login_process)
        self.pwd.returnPressed.connect(self._start_login_process)

        # Links no fundo
        links_layout = QHBoxLayout()
        
        btn_reg = QPushButton("Criar Conta")
        btn_rec = QPushButton("Recuperar")
        
        for b in (btn_reg, btn_rec):
            b.setCursor(QCursor(Qt.PointingHandCursor))
            b.setStyleSheet("""
                QPushButton {
                    background: transparent; color: #aaa; border: none; font-size: 12px;
                }
                QPushButton:hover { color: white; text-decoration: underline; }
            """)
            
        btn_reg.clicked.connect(self.goto_register.emit)
        btn_rec.clicked.connect(self.goto_recover.emit)
        
        links_layout.addWidget(btn_reg)
        links_layout.addStretch()
        links_layout.addWidget(btn_rec)

        # Adicionar tudo ao card
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_sub)
        card_layout.addWidget(self.user)
        card_layout.addWidget(self.pwd)
        
        # Barra de loading entre a password e o botão
        card_layout.addSpacing(5)
        card_layout.addWidget(self.loading_bar)
        card_layout.addSpacing(5)
        
        card_layout.addWidget(self.btn_login)
        card_layout.addStretch()
        card_layout.addLayout(links_layout)
        
        main_layout.addWidget(card)

    def _input_style(self):
        return """
            QLineEdit {
                background-color: #1a1a1a;
                border: 2px solid #333;
                border-radius: 10px;
                padding: 0 15px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
            }
        """

    def _start_login_process(self):
        u = self.user.text().strip()
        p = self.pwd.text().strip()
        
        if not u or not p:
            self.user.setStyleSheet(self._input_style().replace("#333", "#ff4444"))
            self.pwd.setStyleSheet(self._input_style().replace("#333", "#ff4444"))
            return
        
        # 1. UI: Mostrar Loading e Bloquear Botão
        self.loading_bar.show()
        self.btn_login.setText("A VERIFICAR...")
        self.btn_login.setEnabled(False)
        self.user.setEnabled(False)
        self.pwd.setEnabled(False)
        
        # 2. Iniciar Thread de Login (para não congelar a janela)
        self.worker = LoginWorker(self.sm, u, p)
        self.worker.finished.connect(self._handle_login_result)
        self.worker.start()

    def _handle_login_result(self, user):
        # 3. Login terminou: Restaurar UI
        self.loading_bar.hide()
        self.btn_login.setText("ENTRAR")
        self.btn_login.setEnabled(True)
        self.user.setEnabled(True)
        self.pwd.setEnabled(True)
        
        if user:
            # Sucesso!
            self.login_success.emit(user)
        else:
            # Falha
            QMessageBox.critical(self, "Erro", "Credenciais inválidas.")
            self.pwd.clear()
            self.pwd.setFocus()