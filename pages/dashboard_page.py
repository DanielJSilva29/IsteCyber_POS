from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DashboardPage(QWidget):
    """Dashboard com gráficos de faturação."""
    def __init__(self, system_manager):
        super().__init__()
        self.sm = system_manager
        self._build()
        self.refresh()

    def _build(self):
        v = QVBoxLayout(self)
        title = QLabel("Dashboard de Vendas")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        v.addWidget(title)

        self.fig1 = Figure(figsize=(5, 3))
        self.canvas1 = FigureCanvas(self.fig1)
        self.canvas1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        v.addWidget(self.canvas1)

        self.fig2 = Figure(figsize=(5, 3))
        self.canvas2 = FigureCanvas(self.fig2)
        self.canvas2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        v.addWidget(self.canvas2)

    def refresh(self):
        monthly = self.sm.monthly_totals()
        self.fig1.clear()
        ax1 = self.fig1.add_subplot(111)
        if monthly:
            labels = sorted(monthly.keys())
            values = [monthly[k] for k in labels]
            ax1.bar(labels, values)
            ax1.set_title("Total faturado por mês")
            ax1.set_ylabel("€")
            ax1.tick_params(axis='x', rotation=45)
        else:
            ax1.text(0.5, 0.5, "Sem dados de vendas", ha="center", va="center")
        self.canvas1.draw()

        by_seller = self.sm.totals_by_seller()
        self.fig2.clear()
        ax2 = self.fig2.add_subplot(111)
        if by_seller:
            labels = list(by_seller.keys())
            values = [by_seller[k] for k in labels]
            ax2.bar(labels, values)
            ax2.set_title("Total faturado por vendedor")
            ax2.set_ylabel("€")
        else:
            ax2.text(0.5, 0.5, "Sem dados de vendas", ha="center", va="center")
        self.canvas2.draw()
