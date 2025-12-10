from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class DashboardPage(QWidget):
    """Dashboard com gráficos de faturação (Visual Dark Mode)."""
    
    def __init__(self, system_manager, current_user: dict):
        super().__init__()
        self.sm = system_manager
        self.user = current_user
        
        # Configurar matplotlib para dark mode
        plt.style.use('dark_background')
        
        self._build()
        self.refresh()

    def _build(self):
        v = QVBoxLayout(self)
        v.setSpacing(20)
        
        # --- Cabeçalho ---
        company_name = self.user.get("company", "Sua Loja")
        title = QLabel(f"Dashboard - {company_name}")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #fff;")
        v.addWidget(title)

        # --- Cartões de Resumo (KPIs) ---
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        self.card_total = self._create_card("Total Faturado (Mês)", "0.00€", "#28a745") # Verde
        self.card_top_seller = self._create_card("Melhor Vendedor", "-", "#17a2b8") # Azul
        
        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_top_seller)
        v.addLayout(cards_layout)

        # --- Gráficos ---
        charts_layout = QHBoxLayout()
        
        # Gráfico 1
        chart1_frame = QFrame()
        chart1_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 10px; border: 1px solid #444;")
        l1 = QVBoxLayout(chart1_frame)
        self.fig1 = Figure(figsize=(5, 3), facecolor='#2a2a2a')
        self.canvas1 = FigureCanvas(self.fig1)
        self.canvas1.setStyleSheet("background-color: #2a2a2a;")
        l1.addWidget(self.canvas1)
        
        # Gráfico 2
        chart2_frame = QFrame()
        chart2_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 10px; border: 1px solid #444;")
        l2 = QVBoxLayout(chart2_frame)
        self.fig2 = Figure(figsize=(5, 3), facecolor='#2a2a2a')
        self.canvas2 = FigureCanvas(self.fig2)
        self.canvas2.setStyleSheet("background-color: #2a2a2a;")
        l2.addWidget(self.canvas2)

        charts_layout.addWidget(chart1_frame)
        charts_layout.addWidget(chart2_frame)
        
        v.addLayout(charts_layout, 1) # Stretch factor 1 para ocupar espaço

    def _create_card(self, title_text, value_text, color):
        """Cria um cartão visual para totais."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border-radius: 10px;
                border-left: 5px solid {color};
                border: 1px solid #444;
            }}
        """)
        l = QVBoxLayout(card)
        lbl_title = QLabel(title_text)
        lbl_title.setStyleSheet("color: #aaa; font-size: 14px;")
        lbl_val = QLabel(value_text)
        lbl_val.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        lbl_val.setObjectName("valueLabel") # Para encontrar depois
        
        l.addWidget(lbl_title)
        l.addWidget(lbl_val)
        return card

    def refresh(self):
        # 1. Filtros de Loja
        my_company = self.user.get("company")
        my_shop_type = self.user.get("shop_type")
        allowed_sellers = self.sm.get_shop_sellers(my_company, my_shop_type)
        
        # 2. Dados
        monthly = self.sm.monthly_totals(allowed_sellers=allowed_sellers)
        by_seller = self.sm.totals_by_seller(allowed_sellers=allowed_sellers)
        
        # 3. Atualizar Cartões KPI
        total_val = sum(monthly.values()) if monthly else 0
        self.card_total.findChild(QLabel, "valueLabel").setText(f"{total_val:.2f}€")
        
        top_seller = max(by_seller, key=by_seller.get) if by_seller else "-"
        self.card_top_seller.findChild(QLabel, "valueLabel").setText(top_seller)

        # 4. Gráfico 1: Vendas por Mês
        self.fig1.clear()
        ax1 = self.fig1.add_subplot(111)
        ax1.set_facecolor('#2a2a2a') # Fundo do plot
        
        if monthly:
            labels = sorted(monthly.keys())
            values = [monthly[k] for k in labels]
            bars = ax1.bar(labels, values, color="#5c6bc0", zorder=3)
            ax1.set_title("Total Faturado (Mês)", color='white', fontsize=10)
            ax1.tick_params(colors='white', which='both')
            ax1.grid(color='#444', linestyle='--', axis='y', zorder=0)
            
            # Remover bordas feias
            for spine in ax1.spines.values():
                spine.set_color('#444')

            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.0f}€', ha='center', va='bottom', color='white', fontsize=8)
        else:
            ax1.text(0.5, 0.5, "Sem dados", ha="center", va="center", color="#555")
            ax1.axis('off')
            
        self.canvas1.draw()

        # 5. Gráfico 2: Por Vendedor
        self.fig2.clear()
        ax2 = self.fig2.add_subplot(111)
        ax2.set_facecolor('#2a2a2a')
        
        if by_seller:
            labels = list(by_seller.keys())
            values = [by_seller[k] for k in labels]
            bars = ax2.bar(labels, values, color="#26a69a", zorder=3)
            ax2.set_title("Top Vendedores", color='white', fontsize=10)
            ax2.tick_params(colors='white', which='both')
            ax2.grid(color='#444', linestyle='--', axis='y', zorder=0)
            
            for spine in ax2.spines.values():
                spine.set_color('#444')
                
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.0f}€', ha='center', va='bottom', color='white', fontsize=8)
        else:
            ax2.text(0.5, 0.5, "Sem dados", ha="center", va="center", color="#555")
            ax2.axis('off')
            
        self.canvas2.draw()