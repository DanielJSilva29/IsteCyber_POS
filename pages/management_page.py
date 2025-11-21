from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QMessageBox,
    QListWidgetItem, QLabel, QFrame, QFileDialog, QInputDialog
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from models.product import Product

class ManagementPage(QWidget):
    """Página de Gestão para o Administrador."""
    goto_sales = pyqtSignal()
    goto_stats = pyqtSignal()

    def __init__(self, system_manager, admin_user: dict):
        super().__init__()
        self.sm = system_manager
        self.admin = admin_user      # <- admin atual (tem company e shop_type)
        self._build()
        self._refresh_lists()

    def _ptype_options(self):
        """Devolve a lista de tipos de produto consoante o tipo de loja."""
        st = self.admin.get("shop_type", "OUTRO")

        if st == "RESTAURACAO":
            return ["Bebida", "Prato", "Sobremesa", "Entrada", "Café", "Outro"]
        elif st == "FARMACIA":
            return ["Medicamento", "Suplemento", "Higiene", "Cosmético", "Dispositivo", "Outro"]
        elif st == "OFICINA":
            return ["Peça", "Mão-de-obra", "Óleo", "Pneu", "Diagnóstico", "Outro"]
        else:  # OUTRO
            return ["Produto", "Serviço", "Outro"]



    def _build(self):
        root = QVBoxLayout(self)

        top = QHBoxLayout()
        title = QLabel("Gestão da Loja")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        btn_sales = QPushButton("Ir para Vendas")
        btn_sales.setIcon(QIcon("icons/product.png"))
        btn_stats = QPushButton("Dashboard")
        btn_stats.setIcon(QIcon("icons/stats.png"))
        for b in (btn_sales, btn_stats):
            b.setCursor(Qt.PointingHandCursor)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(btn_sales)
        top.addWidget(btn_stats)

        center = QHBoxLayout()

        # Card de vendedores
        users_card = QFrame()
        users_card.setObjectName("usersCard")
        users_card.setStyleSheet(
            "#usersCard {"
            "  background-color: #2a2a2a;"
            "  border-radius: 10px;"
            "  border: 1px solid #444;"
            "  padding: 10px;"
            "}"
        )
        u_layout = QVBoxLayout(users_card)
        u_title = QLabel("Vendedores")
        u_title.setStyleSheet("font-weight: bold;")
        self.users_list = QListWidget()
        btn_add_vendor = QPushButton("Adicionar Vendedor")
        btn_add_vendor.setIcon(QIcon("icons/user.png"))
        btn_add_vendor.setCursor(Qt.PointingHandCursor)
        u_layout.addWidget(u_title)
        u_layout.addWidget(self.users_list)
        u_layout.addWidget(btn_add_vendor)

        # Card de produtos
        prod_card = QFrame()
        prod_card.setObjectName("productsCard")
        prod_card.setStyleSheet(
            "#productsCard {"
            "  background-color: #2a2a2a;"
            "  border-radius: 10px;"
            "  border: 1px solid #444;"
            "  padding: 10px;"
            "}"
        )
        p_layout = QVBoxLayout(prod_card)
        p_title = QLabel("Produtos")
        p_title.setStyleSheet("font-weight: bold;")
        self.products_list = QListWidget()
        self.products_list.itemDoubleClicked.connect(self._edit_product_dialog)
        btn_add_product = QPushButton("Adicionar Produto")
        btn_add_product.setIcon(QIcon("icons/add.png"))
        btn_add_product.setCursor(Qt.PointingHandCursor)
        btn_export_csv = QPushButton("Exportar vendas CSV")
        btn_export_csv.setCursor(Qt.PointingHandCursor)
        p_layout.addWidget(p_title)
        p_layout.addWidget(self.products_list)
        p_layout.addWidget(btn_add_product)
        p_layout.addWidget(btn_export_csv)

        center.addWidget(users_card, 1)
        center.addSpacing(10)
        center.addWidget(prod_card, 2)

        root.addLayout(top)
        root.addSpacing(10)
        root.addLayout(center)

        btn_sales.clicked.connect(self.goto_sales.emit)
        btn_stats.clicked.connect(self.goto_stats.emit)
        btn_add_vendor.clicked.connect(self._add_vendor_dialog)
        btn_add_product.clicked.connect(self._add_product_dialog)
        btn_export_csv.clicked.connect(self._export_csv)

    def _refresh_lists(self):
        shop_type = self.admin.get("shop_type")
        company = self.admin.get("company")

        # Vendedores apenas desta loja / tipo
        self.users_list.clear()
        for u in self.sm.list_users():
            if u["role"] == "VENDOR" and u.get("shop_type") == shop_type and u.get("company") == company:
                item = QListWidgetItem(u["username"])
                item.setIcon(QIcon(u.get("photo_path") or "icons/user.png"))
                self.users_list.addItem(item)

        # Produtos apenas desta loja / tipo
        self.products_list.clear()
        for p in self.sm.list_products():
            if p.get("shop_type") != shop_type or p.get("company") != company:
                continue
            desc = f'{p["code"]} — {p["name"]} ({p["ptype"]}) {p.get("price_no_vat", 0):.2f}€'
            item = QListWidgetItem(desc)
            item.setIcon(QIcon(p.get("image_path") or "icons/product.png"))
            self.products_list.addItem(item)

    def _add_vendor_dialog(self):
        username, ok = QInputDialog.getText(self, "Novo Vendedor", "Username:")
        if not ok or not username:
            return
        email, ok = QInputDialog.getText(self, "Novo Vendedor", "Email:")
        if not ok or not email:
            return
        pwd, ok = QInputDialog.getText(self, "Novo Vendedor", "Password:")
        if not ok or not pwd:
            return
        try:
            self.sm.add_vendor(
                username=username,
                email=email,
                password=pwd,
                company=self.admin.get("company", ""),
                shop_type=self.admin.get("shop_type", "OUTRO"),
            )
            QMessageBox.information(self, "OK", "Vendedor criado.")
            self._refresh_lists()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def _add_product_dialog(self):
        code, ok = QInputDialog.getText(self, "Produto", "Código:")
        if not ok or not code:
            return
        
        # ✅ Verifica se o código já existe ANTES de pedir os outros dados
        existing_products = self.sm.list_products()
        if any(p.get("code") == code for p in existing_products):
            QMessageBox.warning(self, "Erro", f"Produto com código '{code}' já existe!")
            return
        
        name, ok = QInputDialog.getText(self, "Produto", "Designação:")
        if not ok or not name:
            return
        
        price, ok = QInputDialog.getDouble(self, "Produto", "Preço s/IVA:", 0.0, 0)
        if not ok:
            return

        # Opções dependem do tipo de loja
        options = self._ptype_options()
        ptype, ok = QInputDialog.getItem(
            self, "Produto", "Tipo:", options, 0, False
        )
        if not ok:
            return

        image_path, _ = QFileDialog.getOpenFileName(
            self, "Imagem do Produto (opcional)", "images", "Imagens (*.png *.jpg *.jpeg)"
        )

        # ✅ Cria o produto UMA ÚNICA VEZ
        prod = Product(
            code=code,
            name=name,
            price_no_vat=float(price),
            ptype=ptype,
            image_path=image_path or "",
            company=self.admin.get("company", ""),
            shop_type=self.admin.get("shop_type", "OUTRO"),
        )
        
        try:
            self.sm.add_product(prod)
            QMessageBox.information(self, "Sucesso", "Produto criado com sucesso!")
            self._refresh_lists()  # ✅ Atualiza a lista
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao criar produto: {str(e)}")


    def _export_csv(self):
        from PyQt5.QtWidgets import QFileDialog
        from pathlib import Path
        path, _ = QFileDialog.getSaveFileName(self, "Exportar vendas para CSV", "vendas.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            self.sm.export_sales_csv(Path(path))
            QMessageBox.information(self, "Exportado", "Ficheiro CSV criado com sucesso.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def _edit_product_dialog(self, item):
        from PyQt5.QtWidgets import QInputDialog, QFileDialog
        desc = item.text()
        code = desc.split(" — ")[0]
        products = self.sm.list_products()
        prod = next((p for p in products if p["code"] == code), None)
        if not prod:
            QMessageBox.critical(self, "Erro", "Produto não encontrado.")
            return

        name, ok = QInputDialog.getText(self, "Editar produto", "Designação:", text=prod["name"])
        if not ok or not name:
            return
        price, ok = QInputDialog.getDouble(
            self, "Editar produto", "Preço s/IVA:", float(prod.get("price_no_vat", 0.0)), 0
        )
        if not ok:
            return

        options = self._ptype_options()
        # Se o tipo atual existir na lista, usa-o como default, senão começa no 0
        try:
            current_index = options.index(prod.get("ptype", options[0]))
        except ValueError:
            current_index = 0

        ptype, ok = QInputDialog.getItem(
            self, "Editar produto", "Tipo:", options, current_index, False
        )
        if not ok:
            return

        image_path, _ = QFileDialog.getOpenFileName(
            self, "Nova imagem (opcional)", "images", "Imagens (*.png *.jpg *.jpeg)"
        )
        updates = {
            "name": name,
            "price_no_vat": float(price),
            "ptype": ptype,
        }
        if image_path:
            updates["image_path"] = image_path
        try:
            self.sm.update_product(code, **updates)
            QMessageBox.information(self, "OK", "Produto atualizado.")
            self._refresh_lists()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

