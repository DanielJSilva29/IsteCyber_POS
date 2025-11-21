from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QMessageBox,
    QLabel, QListWidgetItem, QLineEdit
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPixmap
from .toast import Toast

class SalesPage(QWidget):
    """Página de Vendas para Vendedor/Admin."""
    back_to_manage = pyqtSignal()

    def __init__(self, system_manager, current_user: dict):
        super().__init__()
        self.sm = system_manager
        self.user = current_user
        self.seller_username = current_user["username"]
        self.shop_type = current_user.get("shop_type")
        self.company = current_user.get("company")
        self.cart = []  # [{code,name,qty,price_no_vat}]
        self._build()

    def _build(self):
        main = QVBoxLayout(self)
        top_bar = QHBoxLayout()
        btn_back = QPushButton("Voltar")
        btn_back.setIcon(QIcon("icons/back.png"))
        btn_back.setCursor(Qt.PointingHandCursor)
        top_bar.addWidget(btn_back)
        top_title = QLabel("Vendas")
        top_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_bar.addWidget(top_title)
        top_bar.addStretch()
        main.addLayout(top_bar)

        center = QHBoxLayout()

        # Esquerda: Carrinho
        left = QVBoxLayout()
        lbl_cart = QLabel("Carrinho / Fatura")
        self.invoice_list = QListWidget()
        btn_remove_item = QPushButton("Remover item selecionado")
        btn_clear = QPushButton("Limpar carrinho")
        btn_confirm = QPushButton("Confirmar e Gerar Fatura")
        left.addWidget(lbl_cart)
        left.addWidget(self.invoice_list)
        left.addWidget(btn_remove_item)
        left.addWidget(btn_clear)
        left.addWidget(btn_confirm)

        # Direita: Produtos
        right = QVBoxLayout()
        lbl_products = QLabel("Produtos disponíveis")
        search_row = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Pesquisar produto...")
        search_row.addWidget(self.search_box)
        right.addWidget(lbl_products)
        right.addLayout(search_row)
        self.products = QListWidget()
        self.product_preview = QLabel()
        self.product_preview.setFixedHeight(150)
        self.product_preview.setStyleSheet("border: 1px solid #555; background: #111;")
        self.product_preview.setAlignment(Qt.AlignCenter)
        right.addWidget(self.products)
        right.addWidget(QLabel("Preview do produto"))
        right.addWidget(self.product_preview)

        center.addLayout(left, 2)
        center.addLayout(right, 3)
        main.addLayout(center)

        self._load_products()

        btn_back.clicked.connect(self.back_to_manage.emit)
        self.products.itemClicked.connect(self._show_preview)
        self.products.itemDoubleClicked.connect(self._add_to_cart)
        btn_confirm.clicked.connect(self._confirm)
        btn_remove_item.clicked.connect(self._remove_selected_item)
        btn_clear.clicked.connect(self._clear_cart)
        self.search_box.textChanged.connect(self._filter_products)

    def _load_products(self):
        all_products = self.sm.list_products()
        # Filtrar por shop_type + company
        self.all_products = [
            p for p in all_products
            if p.get("shop_type") == self.shop_type and p.get("company") == self.company
        ]
        self._populate_products_list(self.all_products)
        self._refresh_invoice_list()

    def _populate_products_list(self, products):
        self.products.clear()
        for p in products:
            desc = f'{p["code"]} — {p["name"]} ({p.get("price_no_vat", 0):.2f}€)'
            item = QListWidgetItem(desc)
            item.setIcon(QIcon(p.get("image_path") or "icons/product.png"))
            item.setData(32, p)  # Qt.UserRole
            self.products.addItem(item)

    def _filter_products(self, text):
        text = text.strip().lower()
        if not text:
            self._populate_products_list(self.all_products)
            return
        filtered = [
            p for p in self.all_products
            if text in p["name"].lower() or text in p["code"].lower()
        ]
        self._populate_products_list(filtered)

    def _show_preview(self, item):
        data = item.data(32)
        img_path = data.get("image_path") if data else None
        if img_path:
            pix = QPixmap(img_path).scaledToHeight(140, Qt.SmoothTransformation)
            self.product_preview.setPixmap(pix)
        else:
            self.product_preview.setPixmap(QPixmap())
            self.product_preview.setText("Sem imagem")

    def _add_to_cart(self, item):
        data = item.data(32)
        if not data:
            return
        code = data["code"]
        prod = data
        for it in self.cart:
            if it["code"] == code:
                it["qty"] += 1
                break
        else:
            self.cart.append({
                "code": code,
                "name": prod["name"],
                "qty": 1,
                "price_no_vat": prod.get("price_no_vat", 0.0),
            })
        self._refresh_invoice_list()
        Toast(self, f"Adicionado: {prod['name']}")

    def _refresh_invoice_list(self):
        self.invoice_list.clear()
        total = sum(i["qty"] * i["price_no_vat"] for i in self.cart)
        for i in self.cart:
            self.invoice_list.addItem(
                f'{i["name"]} x{i["qty"]} @ {i["price_no_vat"]:.2f}€'
            )
        self.invoice_list.addItem(f'— Total s/IVA: {total:.2f}€')
        self.invoice_list.addItem(f'— Total c/IVA(23%): {total*1.23:.2f}€')

    def _remove_selected_item(self):
        row = self.invoice_list.currentRow()
        if row < 0 or row >= len(self.cart):
            QMessageBox.warning(self, "Aviso", "Selecione um item do carrinho (não o total).")
            return
        item = self.cart[row]
        reply = QMessageBox.question(self, "Confirmar", f"Remover '{item['name']}' do carrinho?")
        if reply == QMessageBox.Yes:
            self.cart.pop(row)
            self._refresh_invoice_list()

    def _clear_cart(self):
        if not self.cart:
            return
        reply = QMessageBox.question(self, "Confirmar", "Tem a certeza que deseja limpar o carrinho?")
        if reply == QMessageBox.Yes:
            self.cart.clear()
            self._refresh_invoice_list()

    def _confirm(self):
        if not self.cart:
            QMessageBox.warning(self, "Aviso", "Carrinho vazio.")
            return
        invoice = self.sm.create_invoice(
            items=self.cart,
            seller_username=self.seller_username,
            vat_rate=0.23,
        )
        msg = f'Fatura emitida. Total: {invoice["total_with_vat"]:.2f}€\n'
        if "html_path" in invoice:
            msg += f'Fatura HTML em: {invoice["html_path"]}'
        QMessageBox.information(self, "Fatura emitida", msg)
        self.cart.clear()
        self._refresh_invoice_list()
