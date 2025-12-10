"""SystemManager: persistência em JSON e regras de negócio do POS."""
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import csv

from .admin import Admin
from .vendor import Vendor
from .product import Product

# Diretórios base
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
INVOICE_DIR = ROOT_DIR / "invoices"


class SystemManager:
    """Classe responsável por gerir utilizadores, produtos e vendas."""

    USERS = DATA_DIR / "users.json"
    PRODUCTS = DATA_DIR / "products.json"
    SALES = DATA_DIR / "sales.json"
    
    def get_shop_sellers(self, company: str, shop_type: str) -> List[str]:
        """Retorna uma lista de usernames de vendedores que pertencem a uma loja específica."""
        users = self.list_users()
        sellers = []
        for u in users:
            # Verifica se é vendedor e se pertence à empresa/tipo de loja
            if (u.get("role") == "VENDOR" and 
                u.get("company") == company and 
                u.get("shop_type") == shop_type):
                sellers.append(u.get("username"))
        # Incluir também os admins dessa loja, caso eles façam vendas
        for u in users:
             if (u.get("role") == "ADMIN" and 
                u.get("company") == company and 
                u.get("shop_type") == shop_type):
                sellers.append(u.get("username"))
        return sellers

    def __init__(self) -> None:
        DATA_DIR.mkdir(exist_ok=True)
        INVOICE_DIR.mkdir(exist_ok=True)
        for f in (self.USERS, self.PRODUCTS, self.SALES):
            if not f.exists():
                f.write_text("[]", encoding="utf-8")

    # ---------- Helpers JSON ----------
    def _load_json(self, path: Path) -> list:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save_json(self, path: Path, data: list) -> None:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ---------- Utilizadores ----------
    def register_admin(
        self,
        *,
        company: str,
        vat: str,
        shop_type: str,
        username: str,
        email: str,
        password: str,
        photo_path: str = "",
    ) -> Dict:
        """Regista um novo Administrador."""
        users = self._load_json(self.USERS)
        if any(u["username"].lower() == username.lower() for u in users):
            raise ValueError("Username já existe.")
        admin = Admin(username=username, email=email, password=password)
        payload = admin.to_dict() | {
            "company": company,
            "vat": vat,
            "shop_type": shop_type,
            "photo_path": photo_path,
        }
        users.append(payload)
        self._save_json(self.USERS, users)
        return payload

    def add_vendor(
        self,
        *,
        username: str,
        email: str,
        password: str,
        company: str,
        shop_type: str,
        photo_path: str = "",
    ) -> Dict:
        """
        Adiciona um novo vendedor ao sistema, associado a uma loja.

        O vendedor fica marcado com:
        - company
        - shop_type (RESTAURACAO, FARMACIA, OFICINA, OUTRO)
        """
        users = self._load_json(self.USERS)
        if any(u["username"].lower() == username.lower() for u in users):
            raise ValueError("Username já existe.")
        vendor = Vendor(username=username, email=email, password=password)
        payload = vendor.to_dict() | {
            "photo_path": photo_path,
            "company": company,
            "shop_type": shop_type,
        }
        users.append(payload)
        self._save_json(self.USERS, users)
        return payload

    def list_users(self) -> List[Dict]:
        """Devolve a lista de utilizadores.

        O ficheiro users.json é guardado como uma LISTA simples de dicts.
        """
        data = self._load_json(self.USERS)

        # Caso "normal": é uma lista de utilizadores
        if isinstance(data, list):
            return data

        # Se por acaso estiver no formato {"users": [...]}, também lidamos com isso
        if isinstance(data, dict) and isinstance(data.get("users"), list):
            return data["users"]

        return []


    def login(self, username: str, password: str):
        """
        Autentica um utilizador.
        """
        try:
            users = self.list_users()
            
            # Verifica se users é realmente uma lista
            if not isinstance(users, list):
                return None
            
            for u in users:
                # Verifica se u é um dicionário
                if not isinstance(u, dict):
                    continue
                
                # Compara username e password
                if u.get("username", "").lower() == username.lower() and u.get("password") == password:
                    return u
            
            return None
        
        except Exception as e:
            print(f"Erro no login: {e}")
            return None


    # ---------- Produtos ----------
    def add_product(self, p: Product) -> Dict:
        """
        Adiciona um novo produto.

        O código só tem de ser único dentro da mesma empresa + tipo de loja.
        Permite ter código "01" em RESTAURACAO e "01" em FARMACIA, por exemplo.
        """
        products = self._load_json(self.PRODUCTS)

        for x in products:
            if (
                x["code"].lower() == p.code.lower()
                and x.get("company") == p.company
                and x.get("shop_type") == p.shop_type
            ):
                raise ValueError("Código de produto duplicado nesta loja.")

        payload = p.to_dict()
        products.append(payload)
        self._save_json(self.PRODUCTS, products)
        return payload

    def update_product(self, code: str, **updates) -> Dict:
        """Atualiza campos de um produto (por código)."""
        products = self._load_json(self.PRODUCTS)
        found = None
        for p in products:
            if p["code"].lower() == code.lower():
                for k, v in updates.items():
                    if v is not None:
                        p[k] = v
                found = p
                break
        if found is None:
            raise ValueError("Produto não encontrado.")
        self._save_json(self.PRODUCTS, products)
        return found

    def list_products(self) -> List[Dict]:
        """Devolve a lista completa de produtos (filtragem é feita nas páginas)."""
        return self._load_json(self.PRODUCTS)

    def adjust_stock(self, code: str, delta: int) -> Dict:
        """Altera o stock de um produto (delta pode ser positivo ou negativo)."""
        products = self._load_json(self.PRODUCTS)
        for p in products:
            if p["code"].lower() == code.lower():
                p["stock"] = int(p.get("stock", 0)) + int(delta)
                if p["stock"] < 0:
                    p["stock"] = 0
                self._save_json(self.PRODUCTS, products)
                return p
        raise ValueError("Produto não encontrado.")

    # ---------- Vendas / Faturas ----------
    def create_invoice(
        self,
        *,
        items: List[Dict],
        seller_username: str,
        vat_rate: float = 0.23,
    ) -> Dict:
        """Cria uma fatura, VALIDA STOCK, desconta stock e gera HTML."""
        
        # 1. Validação de Stock (Antes de processar qualquer coisa)
        products = self._load_json(self.PRODUCTS)
        product_map = {p["code"]: p for p in products} # Mapa para acesso rápido

        for item in items:
            code = item["code"]
            qty_needed = item["qty"]
            
            # Encontrar produto na base de dados para ver o stock real
            # Nota: Num cenário real, devíamos filtrar também por company/shop_type para garantir unicidade
            prod_db = None
            for p in products:
                if p["code"] == code: # Assumindo código único ou lógica de filtro prévia
                    prod_db = p
                    break
            
            if not prod_db:
                raise ValueError(f"Produto {code} não encontrado na base de dados.")
            
            current_stock = int(prod_db.get("stock", 0))
            if current_stock < qty_needed:
                raise ValueError(f"Stock insuficiente para '{prod_db['name']}'. Stock atual: {current_stock}")

        # 2. Se passou a validação, descontar o stock
        for item in items:
            self.adjust_stock(item["code"], -item["qty"])

        # 3. Criar a fatura (Código original)
        total_no_vat = round(
            sum(i["qty"] * i["price_no_vat"] for i in items), 2
        )
        total_vat = round(total_no_vat * vat_rate, 2)
        total_with_vat = round(total_no_vat + total_vat, 2)
        now = datetime.now()
        invoice_id = now.strftime("INV%Y%m%d%H%M%S")
        invoice = {
            "id": invoice_id,
            "timestamp": now.isoformat(),
            "seller": seller_username,
            "items": items,
            "total_no_vat": total_no_vat,
            "vat_rate": vat_rate,
            "total_with_vat": total_with_vat,
        }

        sales = self._load_json(self.SALES)
        sales.append(invoice)
        self._save_json(self.SALES, sales)

        # Gerar HTML
        html_path = INVOICE_DIR / f"{invoice_id}.html"
        self._generate_invoice_html(invoice, html_path)
        invoice["html_path"] = str(html_path)

        # Atualizar registo com caminho do HTML
        sales = self._load_json(self.SALES)
        for s in sales:
            if s.get("id") == invoice_id:
                s["html_path"] = invoice["html_path"]
        self._save_json(self.SALES, sales)

        return invoice

    def _generate_invoice_html(self, invoice: Dict, path: Path) -> None:
        """Gera um ficheiro HTML bonito para a fatura."""
        seller = invoice["seller"]
        date_str = datetime.fromisoformat(invoice["timestamp"]).strftime(
            "%d/%m/%Y %H:%M"
        )
        rows = ""
        for it in invoice["items"]:
            subtotal = it["qty"] * it["price_no_vat"]
            rows += (
                f"<tr>"
                f"<td>{it['code']}</td>"
                f"<td>{it['name']}</td>"
                f"<td>{it['qty']}</td>"
                f"<td>{it['price_no_vat']:.2f}€</td>"
                f"<td>{subtotal:.2f}€</td>"
                f"</tr>"
            )

        html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Fatura {invoice['id']}</title>
<style>
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background:#f5f5f5;
}}
.invoice-container {{
  max-width: 800px;
  margin:40px auto;
  background:#fff;
  padding:24px;
  border-radius:8px;
  box-shadow:0 4px 12px rgba(0,0,0,0.08);
}}
.header {{
  display:flex;
  justify-content:space-between;
  margin-bottom:20px;
}}
.header-left h1 {{
  margin:0;
  font-size:24px;
}}
.header-right {{
  text-align:right;
  font-size:14px;
  color:#555;
}}
table {{
  width:100%;
  border-collapse:collapse;
  margin-top:20px;
}}
th, td {{
  border-bottom:1px solid #ddd;
  padding:8px;
  text-align:left;
  font-size:14px;
}}
th {{
  background:#fafafa;
}}
.totals {{
  margin-top:20px;
  float:right;
  font-size:14px;
}}
.totals div {{
  display:flex;
  justify-content:space-between;
}}
.footer {{
  clear:both;
  margin-top:40px;
  font-size:12px;
  color:#777;
  text-align:center;
}}
</style>
</head>
<body>
<div class="invoice-container">
  <div class="header">
    <div class="header-left">
      <h1>Fatura</h1>
      <div>Nº: {invoice['id']}</div>
    </div>
    <div class="header-right">
      <div>Data: {date_str}</div>
      <div>Responsável: {seller}</div>
    </div>
  </div>
  <table>
    <thead>
      <tr>
        <th>Código</th>
        <th>Produto</th>
        <th>Qtd</th>
        <th>Preço s/ IVA</th>
        <th>Subtotal</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
  <div class="totals">
    <div><span>Total s/ IVA:</span><span>{invoice['total_no_vat']:.2f}€</span></div>
    <div><span>IVA ({int(invoice['vat_rate']*100)}%):</span><span>{invoice['total_no_vat']*invoice['vat_rate']:.2f}€</span></div>
    <div><strong>Total c/ IVA:</strong><strong>{invoice['total_with_vat']:.2f}€</strong></div>
  </div>
  <div class="footer">
    Sistema POS - Documento gerado automaticamente.
  </div>
</div>
</body>
</html>"""
        path.write_text(html, encoding="utf-8")

    def list_sales(self) -> List[Dict]:
        """Lista todas as vendas/faturas registadas."""
        return self._load_json(self.SALES)

    # ---------- Relatórios / Export ----------
    def export_sales_csv(self, path: Path) -> None:
        """Exporta vendas para CSV simples (para Excel, etc.)."""
        sales = self.list_sales()
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(
                ["id", "timestamp", "seller", "total_no_vat", "vat_rate", "total_with_vat"]
            )
            for s in sales:
                writer.writerow(
                    [
                        s.get("id"),
                        s.get("timestamp"),
                        s.get("seller"),
                        s.get("total_no_vat"),
                        s.get("vat_rate"),
                        s.get("total_with_vat"),
                    ]
                )

    def monthly_totals(self, allowed_sellers: List[str] = None) -> Dict[str, float]:
        """
        Total faturado por mês. 
        Se allowed_sellers for fornecido, filtra apenas vendas desses utilizadores.
        """
        res: Dict[str, float] = {}
        for s in self.list_sales():
            # Filtro de segurança: Só processa se o vendedor estiver na lista permitida
            if allowed_sellers is not None and s.get("seller") not in allowed_sellers:
                continue

            try:
                dt = datetime.fromisoformat(s["timestamp"])
            except Exception:
                continue
            key = dt.strftime("%Y-%m")
            res[key] = res.get(key, 0.0) + float(s.get("total_with_vat", 0.0))
        return res

    def totals_by_seller(self, allowed_sellers: List[str] = None) -> Dict[str, float]:
        """
        Total faturado por vendedor.
        Se allowed_sellers for fornecido, filtra apenas esses utilizadores.
        """
        res: Dict[str, float] = {}
        for s in self.list_sales():
            seller = s.get("seller", "?")
            
            # Filtro de segurança
            if allowed_sellers is not None and seller not in allowed_sellers:
                continue

            res[seller] = res.get(seller, 0.0) + float(
                s.get("total_with_vat", 0.0)
            )
        return res
    
    def change_user_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Altera a password de um utilizador.

        Retorna True se alterar com sucesso, False caso contrário.
        """
        users = self.list_users()

        # Garantir que é uma lista válida
        if not isinstance(users, list):
            return False

        changed = False

        for user in users:
            if not isinstance(user, dict):
                continue
            if user.get("username") == username:
                # Verificar password antiga
                if user.get("password") != old_password:
                    return False
                # Atualizar
                user["password"] = new_password
                changed = True
                break

        if changed:
            # Guardar como LISTA simples
            self._save_json(self.USERS, users)
            return True

        return False

    def update_user_photo(self, username: str, photo_path: str) -> bool:
        """Atualiza a foto de perfil do utilizador (suporta URL ou caminho local)."""
        users = self.list_users()
        changed = False
        
        # Garantir que é uma lista válida
        if not isinstance(users, list):
            return False

        for u in users:
            if isinstance(u, dict) and u.get("username") == username:
                u["photo_path"] = photo_path
                changed = True
                break
        
        if changed:
            self._save_json(self.USERS, users)
            return True
            
        return False
