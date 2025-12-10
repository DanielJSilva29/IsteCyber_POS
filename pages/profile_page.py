from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, 
    QFileDialog, QMessageBox, QHBoxLayout, QDialog, QFormLayout, 
    QFrame, QInputDialog, QMenu, QGraphicsDropShadowEffect, QGridLayout
)
# ADICIONADO QIcon AQUI EM BAIXO
from PyQt5.QtGui import QPixmap, QCursor, QColor, QIcon
from PyQt5.QtCore import Qt, QSize, QPoint
import os
import urllib.request

class ProfilePage(QWidget):
    """Página de perfil profissional com layout horizontal e foto limpa."""
    
    def __init__(self, system_manager, current_user: dict, on_logout):
        super().__init__()
        self.sm = system_manager
        self.user = current_user
        self.on_logout = on_logout
        self._build_ui()
    
    def _build_ui(self):
        if self.layout(): QWidget().setLayout(self.layout())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignCenter)
        
        # --- Card Principal ---
        card = QFrame()
        card.setMaximumWidth(900) 
        card.setStyleSheet("""
            QFrame#MainCard {
                background-color: #222;
                border-radius: 24px;
                border: 1px solid #333;
            }
        """)
        card.setObjectName("MainCard")
        
        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(30)
        card_layout.setContentsMargins(60, 50, 60, 50)
        
        # ============================================
        # TOPO: FOTO (Esquerda) + INFO (Direita)
        # ============================================
        top_header = QHBoxLayout()
        top_header.setSpacing(40)

        # --- 1. Área da Foto ---
        photo_container = QFrame()
        photo_container.setFixedSize(220, 220)
        photo_container.setStyleSheet("background: transparent; border: none;")

        self.photo_lbl = QLabel(photo_container)
        self.photo_lbl.setGeometry(10, 10, 200, 200)
        self.photo_lbl.setStyleSheet("""
            border-radius: 100px; 
            border: 5px solid #222;
            padding: 2px;
            background-color: #333;
            outline: 1px solid #444;
        """)
        self.photo_lbl.setScaledContents(True)
        self.photo_lbl.setAlignment(Qt.AlignCenter)
        
        btn_edit = QPushButton("📷", photo_container)
        btn_edit.setFixedSize(54, 54)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.move(160, 160) 
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #007bff, stop:1 #0056b3);
                color: white;
                border-radius: 27px;
                font-size: 22px;
                border: 4px solid #222;
            }
            QPushButton:hover {
                background-color: #0056b3;
                margin-top: 1px;
            }
        """)
        btn_edit.clicked.connect(self._change_photo_menu)
        
        top_header.addWidget(photo_container)

        # --- 2. Área de Texto ---
        text_info = QVBoxLayout()
        text_info.setAlignment(Qt.AlignVCenter)
        
        lbl_welcome = QLabel("Bem-vindo,")
        lbl_welcome.setStyleSheet("font-size: 20px; color: #888; font-weight: 500;")
        
        name = self.user.get('username', 'Utilizador')
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-size: 48px; font-weight: 800; color: #fff; line-height: 1.2;")
        
        role = "ADMINISTRADOR" if self.user.get('role') == 'ADMIN' else "VENDEDOR"
        company = self.user.get('company', '').upper()
        lbl_role_badge = QLabel(f"  {role} • {company}  ")
        lbl_role_badge.setFixedHeight(34)
        lbl_role_badge.setStyleSheet("""
            background-color: #333;
            color: #007bff;
            font-weight: 700;
            font-size: 14px;
            border-radius: 17px;
            border: 1px solid #444;
            padding: 0 15px;
        """)
        
        text_info.addWidget(lbl_welcome)
        text_info.addWidget(lbl_name)
        text_info.addSpacing(15)
        
        badge_box = QHBoxLayout()
        badge_box.addWidget(lbl_role_badge)
        badge_box.addStretch()
        text_info.addLayout(badge_box)
        
        top_header.addLayout(text_info)
        top_header.addStretch()
        
        card_layout.addLayout(top_header)
        
        # ============================================
        # SEPARADOR
        # ============================================
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #3a3a3a; margin-top: 30px; margin-bottom: 30px;")
        card_layout.addWidget(line)
        
        # ============================================
        # DETALHES
        # ============================================
        details_grid = QGridLayout()
        details_grid.setSpacing(30)
        
        details_grid.addWidget(self._create_info_box("EMAIL", self.user.get('email', 'N/A'), "📧"), 0, 0)
        details_grid.addWidget(self._create_info_box("TIPO DE NEGÓCIO", self.user.get('shop_type', 'N/A'), "🏪"), 0, 1)
        
        card_layout.addLayout(details_grid)
        card_layout.addStretch()
        
        # ============================================
        # BOTÃO PASSWORD
        # ============================================
        btn_pass = QPushButton(" Alterar Password")
        # Se não tiveres o icon lock.png, o botão funciona na mesma (apenas sem ícone)
        if os.path.exists("icons/lock.png"):
            btn_pass.setIcon(QIcon("icons/lock.png"))
            
        btn_pass.setCursor(Qt.PointingHandCursor)
        btn_pass.setFixedHeight(55)
        btn_pass.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #555;
                color: #aaa;
                border-radius: 12px;
                font-weight: 600;
                font-size: 15px;
                padding: 0 25px;
            }
            QPushButton:hover {
                border: 2px solid #DC3545;
                color: #DC3545;
                background-color: #2a1515;
            }
        """)
        btn_pass.clicked.connect(self._open_change_password_dialog)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_pass)
        btn_layout.addStretch()
        card_layout.addLayout(btn_layout)

        layout.addWidget(card)
        self._load_current_photo()

    def _create_info_box(self, label, value, icon_char):
        box = QFrame()
        box.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 15px;
                border: 1px solid #3a3a3a;
            }
        """)
        l = QHBoxLayout(box)
        l.setContentsMargins(25, 20, 25, 20)
        l.setSpacing(20)
        
        lbl_icon = QLabel(icon_char)
        lbl_icon.setStyleSheet("font-size: 30px; color: #555;")
        
        text_v = QVBoxLayout()
        text_v.setSpacing(5)
        lbl_top = QLabel(label)
        lbl_top.setStyleSheet("color: #777; font-size: 13px; font-weight: 700; letter-spacing: 1px;")
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet("color: #eee; font-size: 18px; font-weight: 500;")
        text_v.addWidget(lbl_top)
        text_v.addWidget(lbl_val)
        
        l.addWidget(lbl_icon)
        l.addLayout(text_v)
        l.addStretch()
        return box

    def _load_current_photo(self):
        photo_path = self.user.get("photo_path", "")
        pixmap = QPixmap()
        try:
            if photo_path.startswith("http"):
                data = urllib.request.urlopen(photo_path, timeout=5).read()
                pixmap.loadFromData(data)
            elif photo_path and os.path.exists(photo_path):
                pixmap.load(photo_path)
            else:
                if os.path.exists("icons/user.png"): pixmap.load("icons/user.png")
        except: pass
        
        if not pixmap.isNull():
            scaled = pixmap.scaled(QSize(200, 200), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.photo_lbl.setPixmap(scaled)
        else:
            self.photo_lbl.setText("")

    def _change_photo_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #333; color: white; border: 1px solid #555; padding: 8px; border-radius: 10px; }
            QMenu::item { padding: 10px 25px; border-radius: 5px; font-size: 14px; }
            QMenu::item:selected { background-color: #007bff; }
        """)
        action_url = menu.addAction("🔗  Link da Internet")
        action_file = menu.addAction("📂  Escolher do PC")
        action = menu.exec_(QCursor.pos())
        if action == action_url: self._set_photo_url()
        elif action == action_file: self._set_photo_file()

    def _set_photo_url(self):
        url, ok = QInputDialog.getText(self, "Foto", "Link da imagem:")
        if ok and url: self._save_photo(url)

    def _set_photo_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Foto", "", "Imagens (*.png *.jpg)")
        if path: self._save_photo(path)

    def _save_photo(self, path):
        if self.sm.update_user_photo(self.user.get("username"), path):
            self.user["photo_path"] = path
            self._load_current_photo()

    def _open_change_password_dialog(self):
        dialog = ChangePasswordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self._change_password(dialog.get_passwords())

    def _change_password(self, passwords):
        old, new, conf = passwords['old'], passwords['new'], passwords['confirm']
        if not all([old, new, conf]) or new != conf or len(new) < 6:
            QMessageBox.warning(self, "Erro", "Dados inválidos (mínimo 6 caracteres).")
            return
        if self.user.get('password') != old:
            QMessageBox.warning(self, "Erro", "Password atual incorreta.")
            return
        if self.sm.change_user_password(self.user.get('username'), old, new):
            self.user['password'] = new
            QMessageBox.information(self, "Sucesso", "Password alterada! Faça login novamente.")
            self.on_logout()

class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova Password")
        self.setFixedSize(400, 350)
        self.setStyleSheet("background-color: #2a2a2a; color: white;")
        self._build()
    
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40,40,40,40)
        
        lbl = QLabel("Alterar Password")
        lbl.setStyleSheet("font-size: 20px; font-weight: bold; border: none;")
        layout.addWidget(lbl)
        
        self.old = self._make_input("Password Atual")
        self.new = self._make_input("Nova Password")
        self.conf = self._make_input("Confirmar Nova")
        
        layout.addWidget(self.old)
        layout.addWidget(self.new)
        layout.addWidget(self.conf)
        layout.addSpacing(10)
            
        btn = QPushButton("Guardar Alterações")
        btn.setFixedHeight(50)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("background: #28a745; color: white; border-radius: 10px; font-weight: bold; font-size: 16px; border: none;")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def _make_input(self, placeholder):
        i = QLineEdit(placeholderText=placeholder)
        i.setEchoMode(QLineEdit.Password)
        i.setFixedHeight(45)
        i.setStyleSheet("background-color: #1a1a1a; border: 2px solid #333; border-radius: 10px; padding: 0 15px; color: white;")
        return i

    def get_passwords(self):
        return {'old': self.old.text(), 'new': self.new.text(), 'confirm': self.conf.text()}