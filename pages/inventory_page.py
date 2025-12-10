from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QInputDialog, QMessageBox, QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

class InventoryPage(QWidget):
    """Página de Inventário (stock)."""
    def __init__(self, system_manager, admin_user: dict):
        super().__init__()
        self.sm = system_manager
        self.admin = admin_user
        self.shop_type = admin_user.get("shop_type")
        self.company = admin_user.get("company")
        self._build()
        self.refresh()

    def _build(self):
        v = QVBoxLayout(self)
        title = QLabel("Inventário")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        v.addWidget(title)

        self.list = QListWidget()
        v.addWidget(self.list)

        buttons = QHBoxLayout()
        self.btn_inc = QPushButton("Adicionar stock")
        self.btn_dec = QPushButton("Remover stock")
        self.btn_edit_min = QPushButton("Definir stock mínimo")
        buttons.addWidget(self.btn_inc)
        buttons.addWidget(self.btn_dec)
        buttons.addWidget(self.btn_edit_min)
        v.addLayout(buttons)

        self.btn_inc.clicked.connect(lambda: self._change_stock(+1))
        self.btn_dec.clicked.connect(lambda: self._change_stock(-1))
        self.btn_edit_min.clicked.connect(self._set_min_stock)

    def refresh(self):
        self.list.clear()
        for p in self.sm.list_products():
            if p.get("shop_type") != self.shop_type or p.get("company") != self.company:
                continue
            stock = int(p.get("stock", 0))
            min_stock = int(p.get("min_stock", 0))
            txt = f'{p["code"]} — {p["name"]} | Stock: {stock} (mín: {min_stock})'
            item = QListWidgetItem(txt)
            img_path = p.get("image_path")
            if img_path and not Path(img_path).is_absolute():
                img_path = str(BASE_DIR / img_path)
            item.setIcon(QIcon(img_path or str(BASE_DIR / "icons" / "product.png")))
            if stock < min_stock:
                item.setForeground(Qt.red)
            item.setData(32, p)
            self.list.addItem(item)

    def _get_selected_product(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecione um produto.")
            return None
        return item.data(32)

    def _change_stock(self, direction: int):
        p = self._get_selected_product()
        if not p:
            return
        qty, ok = QInputDialog.getInt(self, "Quantidade", "Quantidade:", 1, 1, 1000, 1)
        if not ok:
            return
        delta = qty * direction
        updated = self.sm.adjust_stock(p["code"], delta)
        QMessageBox.information(self, "Stock atualizado", f'Novo stock de {updated["name"]}: {updated["stock"]}')
        self.refresh()

    def _set_min_stock(self):
        p = self._get_selected_product()
        if not p:
            return
        value, ok = QInputDialog.getInt(self, "Stock mínimo", "Novo stock mínimo:",
                                        int(p.get("min_stock", 0)), 0, 100000, 1)
        if not ok:
            return
        self.sm.update_product(p["code"], min_stock=value)
        self.refresh()