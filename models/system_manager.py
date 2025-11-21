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
        data = self._load_json(self.USERS)
        return data.get("users", [])  # ✅ Retorna APENAS a lista dentro da chave "users"


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
        """Cria uma fatura, guarda em JSON e gera HTML profissional."""
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

    def monthly_totals(self) -> Dict[str, float]:
        """
        Total faturado por mês (YYYY-MM -> €).

        Usado na dashboard para o gráfico de barras.
        """
        res: Dict[str, float] = {}
        for s in self.list_sales():
            try:
                dt = datetime.fromisoformat(s["timestamp"])
            except Exception:
                continue
            key = dt.strftime("%Y-%m")
            res[key] = res.get(key, 0.0) + float(s.get("total_with_vat", 0.0))
        return res

    def totals_by_seller(self) -> Dict[str, float]:
        """Total faturado por vendedor (para gráfico na dashboard)."""
        res: Dict[str, float] = {}
        for s in self.list_sales():
            seller = s.get("seller", "?")
            res[seller] = res.get(seller, 0.0) + float(
                s.get("total_with_vat", 0.0)
            )
        return res
    
    def change_user_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Altera a password de um utilizador.
        
        Args:
            username: Username do utilizador
            old_password: Password atual
            new_password: Nova password
        
        Returns:
            True se alterado com sucesso, False caso contrário
        """
        print(f"\n=== SystemManager.change_user_password ===")
        print(f"Username recebido: {username}")
        
        try:
            print("Carregando utilizadores...")
            # ✅ Usa list_users() em vez de load_users()
            users = self.list_users()
            print(f"Total de utilizadores carregados: {len(users)}")
            
            # DEBUG: Mostra todos os usernames
            print("Usernames disponíveis:", [u.get('username') for u in users])
            
            user_found = False
            
            for user in users:
                if user.get('username') == username:
                    user_found = True
                    print(f"✓ Username encontrado!")
                    
                    # Verifica password antiga
                    if user.get('password') != old_password:
                        print("❌ Password antiga não coincide!")
                        return False
                    
                    print("✓ Password antiga correta!")
                    
                    # Atualiza password
                    user['password'] = new_password
                    print(f"✓ Password atualizada para: {new_password}")
                    
                    # ✅ Guarda usando o método correto do sistema
                    # Verifica se existe um método para guardar
                    if hasattr(self, 'save_users'):
                        self.save_users(users)
                        print("✓ save_users() executado")
                    elif hasattr(self, 'update_user'):
                        self.update_user(user)
                        print("✓ update_user() executado")
                    else:
                        # Guarda diretamente no ficheiro JSON
                        import json
                        from pathlib import Path
                        
                        data_file = Path(__file__).parent.parent / "data" / "users.json"
                        
                        with open(data_file, 'w', encoding='utf-8') as f:
                            json.dump({"users": users}, f, indent=2, ensure_ascii=False)
                        
                        print("✓ Ficheiro JSON atualizado diretamente")
                    
                    return True
            
            if not user_found:
                print(f"❌ Username '{username}' não encontrado!")
            
            return False
        
        except Exception as e:
            print(f"❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
            return False
