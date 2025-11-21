from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QFileDialog, QMessageBox, QComboBox, QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class RegisterPage(QWidget):
    """Página de registo de novo Administrador."""
    def __init__(self, system_manager, on_back):
        super().__init__()
        self.sm = system_manager
        self.on_back = on_back
        self.photo_path = ""
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)
        root.addItem(QSpacerItem(40, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))

        card = QFrame()
        card.setObjectName("registerCard")
        card.setStyleSheet(
            "#registerCard {"
            "  background-color: #2a2a2a;"
            "  border-radius: 12px;"
            "  padding: 24px;"
            "  border: 1px solid #444;"
            "}"
        )
        main = QVBoxLayout(card)
        title = QLabel("Registo de Administrador")
        subtitle = QLabel("Preencha os dados da sua Empresa")
        title.setAlignment(Qt.AlignCenter)
        subtitle.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        subtitle.setStyleSheet("color: #aaa;")

        center = QHBoxLayout()

        # Coluna da Foto
        photo_col = QVBoxLayout()
        photo_label_title = QLabel("Foto do Administrador")
        photo_label_title.setStyleSheet("font-weight: bold;")
        self.photo_lbl = QLabel("Sem foto")
        self.photo_lbl.setAlignment(Qt.AlignCenter)
        self.photo_lbl.setFixedSize(160, 160)
        self.photo_lbl.setStyleSheet("border: 1px dashed #555; background: #1b1b1b;")
        btn_photo = QPushButton("Selecionar Foto")
        btn_photo.setCursor(Qt.PointingHandCursor)
        photo_col.addWidget(photo_label_title)
        photo_col.addWidget(self.photo_lbl)
        photo_col.addWidget(btn_photo)
        photo_col.addStretch()

        # Coluna do formulário
        form_col = QVBoxLayout()
        self.company = QLineEdit(placeholderText="Nome da empresa")
        self.vat = QLineEdit(placeholderText="Número de contribuinte")
        self.username = QLineEdit(placeholderText="Username")
        self.email = QLineEdit(placeholderText="Email")
        self.pwd = QLineEdit(placeholderText="Password")
        self.pwd.setEchoMode(QLineEdit.Password)
        self.pwd2 = QLineEdit(placeholderText="Confirmar Password")
        self.pwd2.setEchoMode(QLineEdit.Password)
        self.shop_type = QComboBox()
        self.shop_type.addItems(["RESTAURACAO", "FARMACIA", "OFICINA", "OUTRO"])

        for w in (self.company, self.vat, self.username, self.email, self.pwd, self.pwd2, self.shop_type):
            form_col.addWidget(w)

        center.addLayout(photo_col, 1)
        center.addSpacing(20)
        center.addLayout(form_col, 2)

        buttons_row = QHBoxLayout()
        btn_back = QPushButton("Voltar")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_reg = QPushButton("Registar")
        btn_reg.setCursor(Qt.PointingHandCursor)
        buttons_row.addWidget(btn_back)
        buttons_row.addStretch()
        buttons_row.addWidget(btn_reg)

        main.addWidget(title)
        main.addWidget(subtitle)
        main.addSpacing(10)
        main.addLayout(center)
        main.addSpacing(10)
        main.addLayout(buttons_row)

        root.addWidget(card)
        root.addItem(QSpacerItem(40, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))

        btn_photo.clicked.connect(self._pick_photo)
        btn_reg.clicked.connect(self._register)
        btn_back.clicked.connect(self.on_back)

    def _pick_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Foto", "", "Imagens (*.png *.jpg *.jpeg)")
        if path:
            self.photo_path = path
            pix = QPixmap(path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_lbl.setPixmap(pix)
            self.photo_lbl.setText("")

    def _mark(self, widget, ok: bool):
        widget.setStyleSheet("" if ok else "border: 1px solid red;")

    def _register(self):
        fields = [self.company, self.vat, self.username, self.email, self.pwd, self.pwd2]
        valid = True
        for f in fields:
            ok = bool(f.text().strip())
            self._mark(f, ok)
            valid &= ok
        if self.pwd.text() != self.pwd2.text():
            self._mark(self.pwd2, False)
            valid = False
        if not valid:
            QMessageBox.warning(self, "Validação", "Revise os campos a vermelho.")
            return
        try:
            self.sm.register_admin(
                company=self.company.text().strip(),
                vat=self.vat.text().strip(),
                shop_type=self.shop_type.currentText(),
                username=self.username.text().strip(),
                email=self.email.text().strip(),
                password=self.pwd.text(),
                photo_path=self.photo_path,
            )
            QMessageBox.information(self, "Sucesso", "Administrador registado.")
            self.on_back()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
