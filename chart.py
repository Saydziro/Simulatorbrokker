# chart.py
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StockChart:
    def __init__(self, parent):
        self.fig = Figure(figsize=(5, 2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.widget = self.canvas.get_tk_widget()

    def plot(self, history: list, symbol: str):
        self.ax.clear()
        if history:
            self.ax.plot(history, marker='o', markersize=3, color="#1f77b4")
            self.ax.set_title(f"История цен: {symbol}", fontsize=10)
            self.ax.set_ylabel("Цена ($)", fontsize=8)
            self.ax.grid(True, linestyle="--", alpha=0.6)
        else:
            self.ax.text(0.5, 0.5, "Нет данных", transform=self.ax.transAxes, ha="center")
        self.canvas.draw()

    def pack(self, **kwargs):
        self.widget.pack(**kwargs)

    def forget(self):
        self.widget.pack_forget()
