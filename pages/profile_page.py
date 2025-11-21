from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog, QMessageBox, QHBoxLayout, QDialog, QFormLayout, QFrame
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ProfilePage(QWidget):
    """Página de perfil do utilizador."""
    
    def __init__(self, system_manager, current_user: dict, on_logout):
        super().__init__()
        self.sm = system_manager
        self.user = current_user
        self.on_logout = on_logout
        self._build_ui()
    
    def _build_ui(self):
        """Constrói a interface da página."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Card de perfil
        profile_card = QFrame()
        profile_card.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 12px;
                border: 1px solid #444;
                padding: 30px;
            }
        """)
        
        profile_layout = QVBoxLayout(profile_card)
        profile_layout.setSpacing(20)
        
        # Título
        title = QLabel("Meu Perfil")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #eee;")
        profile_layout.addWidget(title)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #444;")
        profile_layout.addWidget(separator)
        
        # Informações do utilizador
        info_layout = QVBoxLayout()
        info_layout.setSpacing(15)
        
        # Username
        username_label = QLabel(f"<b>Username:</b> {self.user.get('username', 'N/A')}")
        username_label.setStyleSheet("font-size: 16px; color: #eee;")
        info_layout.addWidget(username_label)
        
        # Email
        email_label = QLabel(f"<b>Email:</b> {self.user.get('email', 'N/A')}")
        email_label.setStyleSheet("font-size: 16px; color: #eee;")
        info_layout.addWidget(email_label)
        
        # Role
        role = self.user.get('role', 'N/A')
        role_display = "Administrador" if role == "ADMIN" else "Vendedor"
        role_label = QLabel(f"<b>Cargo:</b> {role_display}")
        role_label.setStyleSheet("font-size: 16px; color: #eee;")
        info_layout.addWidget(role_label)
        
        # Tipo de loja (se existir)
        if 'shop_type' in self.user:
            shop_label = QLabel(f"<b>Tipo de Loja:</b> {self.user.get('shop_type', 'N/A')}")
            shop_label.setStyleSheet("font-size: 16px; color: #eee;")
            info_layout.addWidget(shop_label)
        
        profile_layout.addLayout(info_layout)
    
        layout.addWidget(profile_card)
        layout.addStretch()
        
        # ✅ Botão de alterar password no canto inferior esquerdo
        bottom_layout = QHBoxLayout()
        
        btn_change_password = QPushButton("🔒 Alterar Password")
        btn_change_password.setFixedWidth(220)  # Largura fixa
        btn_change_password.setMinimumHeight(45)
        btn_change_password.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
            QPushButton:pressed {
                background-color: #BD2130;
            }
            QPushButton:focus {
                outline: none;
            }
        """)
        btn_change_password.setCursor(Qt.PointingHandCursor)
        btn_change_password.clicked.connect(self._open_change_password_dialog)
        
        # Adiciona à esquerda com espaço vazio à direita
        bottom_layout.addWidget(btn_change_password)
        bottom_layout.addStretch()
        
        layout.addLayout(bottom_layout)

    
    def _open_change_password_dialog(self):
        """Abre o diálogo de alteração de password."""
        dialog = ChangePasswordDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            passwords = dialog.get_passwords()
            self._change_password(passwords)
    
    def _change_password(self, passwords: dict):
        """Processa a alteração de password."""
        old_pwd = passwords['old']
        new_pwd = passwords['new']
        confirm_pwd = passwords['confirm']
        
        # Validações
        if not all([old_pwd, new_pwd, confirm_pwd]):
            QMessageBox.warning(self, "Erro", "Preencha todos os campos!")
            return
        
        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, "Erro", "As passwords novas não coincidem!")
            return
        
        if len(new_pwd) < 6:
            QMessageBox.warning(self, "Erro", "A nova password deve ter no mínimo 6 caracteres!")
            return
        
        # Verifica password antiga
        if self.user.get('password') != old_pwd:
            QMessageBox.warning(self, "Erro", "Password atual incorreta!")
            return
        
        # ✅ Usa username em vez de user_id
        username = self.user.get('username')
        
        if not username:
            QMessageBox.critical(self, "Erro", "Não foi possível identificar o utilizador!")
            return
        
        # Altera a password usando o SystemManager
        try:
            success = self.sm.change_user_password(
                username,
                old_pwd,
                new_pwd
            )
            
            if success:
                # Atualiza a password no objeto user local
                self.user['password'] = new_pwd
                
                QMessageBox.information(
                    self,
                    "Sucesso",
                    "Password alterada com sucesso!\n\nPor segurança, será necessário fazer login novamente."
                )
                
                # Faz logout automático
                self.on_logout()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível alterar a password!")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao alterar password: {str(e)}")



class ChangePasswordDialog(QDialog):
    """Diálogo para alteração de password."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alterar Password")
        self.setModal(True)
        self.setFixedSize(450, 300)
        self._build_ui()
    
    def _build_ui(self):
        """Constrói a interface do diálogo."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        title = QLabel("Alterar Password")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #eee;")
        layout.addWidget(title)
        
        # Formulário
        form = QFormLayout()
        form.setSpacing(15)
        
        # Password antiga
        self.input_old_password = QLineEdit()
        self.input_old_password.setEchoMode(QLineEdit.Password)
        self.input_old_password.setPlaceholderText("Digite a password atual")
        self.input_old_password.setMinimumHeight(40)
        form.addRow("Password Atual:", self.input_old_password)
        
        # Nova password
        self.input_new_password = QLineEdit()
        self.input_new_password.setEchoMode(QLineEdit.Password)
        self.input_new_password.setPlaceholderText("Digite a nova password")
        self.input_new_password.setMinimumHeight(40)
        form.addRow("Nova Password:", self.input_new_password)
        
        # Confirmar nova password
        self.input_confirm_password = QLineEdit()
        self.input_confirm_password.setEchoMode(QLineEdit.Password)
        self.input_confirm_password.setPlaceholderText("Confirme a nova password")
        self.input_confirm_password.setMinimumHeight(40)
        self.input_confirm_password.returnPressed.connect(self.accept)
        form.addRow("Confirmar Nova:", self.input_confirm_password)
        
        layout.addLayout(form)
        layout.addSpacing(10)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setMinimumHeight(45)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        
        btn_confirm = QPushButton("Alterar Password")
        btn_confirm.setMinimumHeight(45)
        btn_confirm.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
            QPushButton:pressed {
                background-color: #BD2130;
            }
            QPushButton:focus {
                outline: none;
            }
        """)
        btn_confirm.clicked.connect(self.accept)

        
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_confirm)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def get_passwords(self):
        """Retorna as passwords inseridas."""
        return {
            'old': self.input_old_password.text(),
            'new': self.input_new_password.text(),
            'confirm': self.input_confirm_password.text()
        }