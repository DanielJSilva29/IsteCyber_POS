from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QMessageBox,
    QLabel, QListWidgetItem, QLineEdit
)
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from .toast import Toast
import urllib.request # <--- Necessário para baixar imagens
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

class SalesPage(QWidget):
    """Página de Vendas com suporte a imagens online."""
    back_to_manage = pyqtSignal()

    def __init__(self, system_manager, current_user: dict):
        super().__init__()
        self.sm = system_manager
        self.user = current_user
        self.seller_username = current_user["username"]
        self.shop_type = current_user.get("shop_type")
        self.company = current_user.get("company")
        self.cart = []
        self._build()

    def _build(self):
        main = QVBoxLayout(self)
        top_bar = QHBoxLayout()
        btn_back = QPushButton("Voltar")
        btn_back.setIcon(QIcon(str(BASE_DIR / "icons" / "back.png")))
        btn_back.setCursor(Qt.PointingHandCursor)
        top_bar.addWidget(btn_back)
        
        loja_nome = self.company if self.company else "Loja"
        top_title = QLabel(f"Vendas - {loja_nome}")
        top_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_bar.addWidget(top_title)
        top_bar.addStretch()
        main.addLayout(top_bar)

        center = QHBoxLayout()

        # Esquerda: Carrinho
        left = QVBoxLayout()
        lbl_cart = QLabel("Carrinho / Fatura")
        lbl_cart.setStyleSheet("font-weight:bold; color:#aaa;")
        
        self.invoice_list = QListWidget()
        self.invoice_list.setIconSize(QSize(40, 40))
        
        btn_remove_item = QPushButton("Remover item selecionado")
        btn_clear = QPushButton("Limpar carrinho")
        btn_confirm = QPushButton("Confirmar e Gerar Fatura")
        btn_confirm.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 10px;")
        
        left.addWidget(lbl_cart)
        left.addWidget(self.invoice_list)
        left.addWidget(btn_remove_item)
        left.addWidget(btn_clear)
        left.addWidget(btn_confirm)

        # Direita: Produtos
        right = QVBoxLayout()
        lbl_products = QLabel("Produtos disponíveis")
        lbl_products.setStyleSheet("font-weight:bold; color:#aaa;")
        
        search_row = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Pesquisar produto...")
        search_row.addWidget(self.search_box)
        
        self.products = QListWidget()
        self.products.setIconSize(QSize(64, 64))
        
        self.product_preview = QLabel()
        self.product_preview.setFixedHeight(200)
        self.product_preview.setStyleSheet("border: 1px solid #444; background: #222; border-radius: 8px;")
        self.product_preview.setAlignment(Qt.AlignCenter)
        
        right.addWidget(lbl_products)
        right.addLayout(search_row)
        right.addWidget(self.products)
        right.addWidget(QLabel("Detalhe do Produto:"))
        right.addWidget(self.product_preview)

        center.addLayout(left, 4)
        center.addLayout(right, 6)
        main.addLayout(center)

        # Carregar produtos (pode demorar um pouco por causa das imagens online)
        self._load_products()

        btn_back.clicked.connect(self.back_to_manage.emit)
        self.products.itemClicked.connect(self._show_preview)
        self.products.itemDoubleClicked.connect(self._add_to_cart)
        btn_confirm.clicked.connect(self._confirm)
        btn_remove_item.clicked.connect(self._remove_selected_item)
        btn_clear.clicked.connect(self._clear_cart)
        self.search_box.textChanged.connect(self._filter_products)

    def _load_icon(self, path):
        """Helper para carregar ícone de ficheiro ou URL."""
        if not path:
            return QIcon(str(BASE_DIR / "icons" / "product.png"))
        
        if path.startswith("http"):
            try:
                # Baixar dados da imagem
                data = urllib.request.urlopen(path, timeout=3).read()
                pix = QPixmap()
                pix.loadFromData(data)
                return QIcon(pix)
            except:
                return QIcon(str(BASE_DIR / "icons" / "product.png"))
        else:
            # Caminho local - verificar se é relativo
            if not Path(path).is_absolute():
                path = str(BASE_DIR / path)
            return QIcon(path)

    def _load_pixmap(self, path):
        """Helper para carregar QPixmap (para o preview)."""
        if not path:
            return QPixmap()
        
        if path.startswith("http"):
            try:
                data = urllib.request.urlopen(path, timeout=3).read()
                pix = QPixmap()
                pix.loadFromData(data)
                return pix
            except:
                return QPixmap()
        else:
            # Caminho local - verificar se é relativo
            if not Path(path).is_absolute():
                path = str(BASE_DIR / path)
            return QPixmap(path)

    def _load_products(self):
        all_products = self.sm.list_products()
        self.all_products = [
            p for p in all_products
            if p.get("shop_type") == self.shop_type and p.get("company") == self.company
        ]
        self._populate_products_list(self.all_products)
        self._refresh_invoice_list()

    def _populate_products_list(self, products):
        self.products.clear()
        for p in products:
            stock = int(p.get("stock", 0))
            price = p.get("price_no_vat", 0)
            
            desc = f"{p['name']}\n{price:.2f}€ | Stock: {stock}"
            item = QListWidgetItem(desc)
            
            # USAR O NOVO HELPER AQUI
            img_path = p.get("image_path", "")
            item.setIcon(self._load_icon(img_path))
            
            item.setData(32, p) 
            
            if stock <= 0:
                item.setFlags(Qt.NoItemFlags)
                item.setText(f"{p['name']} (ESGOTADO)\n{price:.2f}€")
                
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
        
        # USAR O NOVO HELPER AQUI
        pix = self._load_pixmap(img_path)
        
        if not pix.isNull():
            pix = pix.scaled(self.product_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.product_preview.setPixmap(pix)
        else:
            self.product_preview.setPixmap(QPixmap())
            self.product_preview.setText("Sem imagem")

    def _add_to_cart(self, item):
        data = item.data(32)
        if not data: return
        
        code = data["code"]
        stock_max = int(data.get("stock", 0))
        
        qty_in_cart = 0
        target_item = None
        for it in self.cart:
            if it["code"] == code:
                qty_in_cart = it["qty"]
                target_item = it
                break
        
        if qty_in_cart + 1 > stock_max:
            QMessageBox.warning(self, "Stock Insuficiente", f"Stock disponível: {stock_max}")
            return

        if target_item:
            target_item["qty"] += 1
        else:
            self.cart.append({
                "code": code,
                "name": data["name"],
                "qty": 1,
                "price_no_vat": data.get("price_no_vat", 0.0),
                "image_path": data.get("image_path")
            })
            
        self._refresh_invoice_list()
        
        if hasattr(self, 'show_toast'): self.show_toast(f"Adicionado: {data['name']}")
        else: Toast(self, f"Adicionado: {data['name']}", 1000)

    def _refresh_invoice_list(self):
        self.invoice_list.clear()
        total = sum(i["qty"] * i["price_no_vat"] for i in self.cart)
        
        for i in self.cart:
            price = i["price_no_vat"]
            subtotal = price * i["qty"]
            text = f"{i['name']} x{i['qty']}\nUnit: {price:.2f}€ | Sub: {subtotal:.2f}€"
            
            item = QListWidgetItem(text)
            # USAR O NOVO HELPER AQUI TAMBÉM
            item.setIcon(self._load_icon(i.get("image_path")))
                
            self.invoice_list.addItem(item)
            
        self.invoice_list.addItem(f"--------------------------------")
        self.invoice_list.addItem(f"Total s/IVA: {total:.2f}€")
        self.invoice_list.addItem(f"Total c/IVA (23%): {total*1.23:.2f}€")

    def _remove_selected_item(self):
        row = self.invoice_list.currentRow()
        if row < 0 or row >= len(self.cart): return
        item = self.cart[row]
        if item["qty"] > 1: item["qty"] -= 1
        else: self.cart.pop(row)
        self._refresh_invoice_list()

    def _clear_cart(self):
        if not self.cart: return
        self.cart.clear()
        self._refresh_invoice_list()

    def _confirm(self):
        if not self.cart:
            QMessageBox.warning(self, "Aviso", "Carrinho vazio.")
            return
        try:
            invoice = self.sm.create_invoice(
                items=self.cart, seller_username=self.seller_username, vat_rate=0.23,
            )
            msg = f'Fatura emitida com sucesso!\nTotal: {invoice["total_with_vat"]:.2f}€'
            QMessageBox.information(self, "Venda Concluída", msg)
            self.cart.clear()
            self._load_products() 
        except Exception as e:
            QMessageBox.critical(self, "Erro na Venda", str(e))