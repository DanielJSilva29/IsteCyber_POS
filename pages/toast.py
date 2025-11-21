from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve, Qt

class Toast(QLabel):
    """Pequena notificação tipo 'toast' sobreposta na janela."""
    def __init__(self, parent, message: str, timeout: int = 2000):
        super().__init__(parent)
        self.setText(message)
        self.setStyleSheet(
            "background: rgba(0,0,0,0.85); color: white; padding: 6px 10px; "
            "border-radius: 6px; font-size: 12px;"
        )
        self.setWindowFlags(Qt.ToolTip)
        self.adjustSize()
        geo = parent.geometry()
        w = self.width()
        h = self.height()
        x = geo.width() - w - 20
        y = geo.height() - h - 20
        self.setGeometry(QRect(x, y+20, w, h))
        self.show()
        self.raise_()

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(x, y+20, w, h))
        self.anim.setEndValue(QRect(x, y, w, h))
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

        self._timer = self.startTimer(timeout)

    def timerEvent(self, event):
        self.killTimer(self._timer)
        self.close()
