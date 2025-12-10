from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QFileDialog, QMessageBox, QComboBox, QFrame, QGraphicsDropShadowEffect, QScrollArea
)
from PyQt5.QtGui import QPixmap, QColor, QCursor, QIcon
from PyQt5.QtCore import Qt, QSize

class RegisterPage(QWidget):
    """Página de Registo Estilizada."""
    def __init__(self, system_manager, on_back):
        super().__init__()
        self.sm = system_manager
        self.on_back = on_back
        self.photo_path = ""
        self._build()

    def _build(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Scroll area para garantir que cabe em ecrãs pequenos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QWidget { background: transparent; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignCenter)
        
        # Card
        card = QFrame()
        card.setFixedWidth(500)
        card.setStyleSheet("background-color: #2a2a2a; border-radius: 20px; border: 1px solid #333;")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0,0,0,100))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        
        # Header
        lbl_title = QLabel("Criar Conta Admin")
        lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; border: none;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)
        layout.addSpacing(10)
        
        # Foto Upload (Botão Redondo)
        photo_container = QHBoxLayout()
        self.photo_btn = QPushButton("📷")
        self.photo_btn.setFixedSize(100, 100)
        self.photo_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.photo_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                border: 2px dashed #555;
                border-radius: 50px;
                color: #555;
                font-size: 30px;
            }
            QPushButton:hover {
                border-color: #007bff;
                color: #007bff;
            }
        """)
        self.photo_btn.clicked.connect(self._pick_photo)
        photo_container.addWidget(self.photo_btn)
        layout.addLayout(photo_container)
        
        lbl_photo_hint = QLabel("Adicionar Logótipo/Foto")
        lbl_photo_hint.setAlignment(Qt.AlignCenter)
        lbl_photo_hint.setStyleSheet("color: #666; font-size: 12px; border: none;")
        layout.addWidget(lbl_photo_hint)
        layout.addSpacing(10)

        # Campos
        self.company = self._make_input("Nome da Empresa")
        self.vat = self._make_input("NIF")
        self.username = self._make_input("Username")
        self.email = self._make_input("Email")
        self.pwd = self._make_input("Password", pwd=True)
        self.pwd2 = self._make_input("Confirmar Password", pwd=True)
        
        self.shop_type = QComboBox()
        self.shop_type.addItems(["RESTAURACAO", "FARMACIA", "OFICINA", "OUTRO"])
        self.shop_type.setFixedHeight(45)
        self.shop_type.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a; border: 2px solid #333; border-radius: 10px;
                padding: 0 15px; color: white; font-size: 14px;
            }
            QComboBox::drop-down { border: none; }
        """)
        
        for w in (self.company, self.vat, self.shop_type, self.username, self.email, self.pwd, self.pwd2):
            layout.addWidget(w)
            
        layout.addSpacing(20)
        
        # Botões
        btn_reg = QPushButton("REGISTAR")
        btn_reg.setFixedHeight(50)
        btn_reg.setCursor(QCursor(Qt.PointingHandCursor))
        btn_reg.setStyleSheet("""
            QPushButton {
                background-color: #28a745; color: white; font-weight: bold;
                border-radius: 25px; font-size: 14px; border: none;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        btn_reg.clicked.connect(self._register)
        
        btn_back = QPushButton("Voltar ao Login")
        btn_back.setCursor(QCursor(Qt.PointingHandCursor))
        btn_back.setStyleSheet("""
            QPushButton { background: transparent; color: #888; border: none; }
            QPushButton:hover { color: white; }
        """)
        btn_back.clicked.connect(self.on_back)
        
        layout.addWidget(btn_reg)
        layout.addWidget(btn_back, alignment=Qt.AlignCenter)
        
        content_layout.addWidget(card)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _make_input(self, place, pwd=False):
        i = QLineEdit()
        i.setPlaceholderText(place)
        i.setFixedHeight(45)
        if pwd: i.setEchoMode(QLineEdit.Password)
        i.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a; border: 2px solid #333; border-radius: 10px;
                padding: 0 15px; color: white; font-size: 14px;
            }
            QLineEdit:focus { border: 2px solid #28a745; }
        """)
        return i

    def _pick_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Foto", "", "Images (*.png *.jpg)")
        if path:
            self.photo_path = path
            # Mostrar preview no botão redondo
            pix = QPixmap(path)
            icon = QIcon(pix)
            self.photo_btn.setIcon(icon)
            self.photo_btn.setIconSize(QSize(100, 100))
            self.photo_btn.setText("")
            self.photo_btn.setStyleSheet("border: 2px solid #28a745; border-radius: 50px; background: black;")

    def _register(self):
        try:
            if self.pwd.text() != self.pwd2.text():
                QMessageBox.warning(self, "Erro", "Passwords não coincidem")
                return
            
            self.sm.register_admin(
                company=self.company.text(), vat=self.vat.text(),
                shop_type=self.shop_type.currentText(),
                username=self.username.text(), email=self.email.text(),
                password=self.pwd.text(), photo_path=self.photo_path
            )
            QMessageBox.information(self, "Sucesso", "Conta criada!")
            self.on_back()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))