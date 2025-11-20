# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from models import Portfolio, Market
from data_manager import select_or_create_user, load_data, save_data
from chart import StockChart
from styles import apply_theme

class StockApp:
    def __init__(self, root, username: str):
        self.root = root
        self.username = username
        self.root.title(f"🏦 Симулятор биржи — {username}")
        self.root.geometry("1920x1080")
        self.root.minsize(900, 600)

        self.dark_mode = False
        self.style = ttk.Style()
        self.apply_theme()

        # Загрузка данных текущего пользователя
        self.portfolio, self.market = load_data(username)
        self.selected_stock = None

        self.create_widgets()
        self.update_display()

    def apply_theme(self):
        apply_theme(self.root, self.style, self.dark_mode)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.update_display()

    def create_widgets(self):
        # Верхняя панель
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)
        self.balance_label = ttk.Label(top_frame, font=("Arial", 14, "bold"))
        self.balance_label.pack(side="left")
        self.total_label = ttk.Label(top_frame, font=("Arial", 12))
        self.total_label.pack(side="right")

        # Кнопки
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Купить", command=self.buy_stock).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Продать", command=self.sell_stock).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Новый день", command=self.new_day).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сменить тему", command=self.toggle_theme).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Выход", command=self.on_closing).pack(side="right", padx=5)

        # Ввод
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(input_frame, text="Символ:").pack(side="left")
        self.symbol_entry = ttk.Entry(input_frame, width=10)
        self.symbol_entry.pack(side="left", padx=5)
        ttk.Label(input_frame, text="Кол-во:").pack(side="left")
        self.quantity_entry = ttk.Entry(input_frame, width=8)
        self.quantity_entry.pack(side="left", padx=5)

        # Рынок
        ttk.Label(self.root, text="📈 Рынок акций", font=("Arial", 12, "underline")).pack(pady=(10, 5))
        market_frame = ttk.Frame(self.root, height=160)
        market_frame.pack(fill="x", padx=10, pady=5)
        market_frame.pack_propagate(False)
        cols = ("Символ", "Компания", "Цена ($)")
        self.market_tree = ttk.Treeview(market_frame, columns=cols, show="headings", height=5)
        for col in cols:
            self.market_tree.heading(col, text=col)
            self.market_tree.column(col, width=150)
        self.market_tree.pack(fill="both", expand=True)
        self.market_tree.bind("<<TreeviewSelect>>", self.on_market_select)

        # График
        self.chart = StockChart(self.root)
        self.chart.pack(fill="x", padx=10, pady=5)

        # Портфель
        ttk.Label(self.root, text="💼 Ваш портфель", font=("Arial", 12, "underline")).pack(pady=(10, 5))
        portfolio_frame = ttk.Frame(self.root, height=120)
        portfolio_frame.pack(fill="x", padx=10, pady=5)
        portfolio_frame.pack_propagate(False)
        port_cols = ("Символ", "Кол-во", "Цена", "Стоимость")
        self.portfolio_tree = ttk.Treeview(portfolio_frame, columns=port_cols, show="headings", height=4)
        for col in port_cols:
            self.portfolio_tree.heading(col, text=col)
            self.portfolio_tree.column(col, width=120, anchor="center")
        self.portfolio_tree.pack(fill="both", expand=True)

        # История
        ttk.Label(self.root, text="📋 История операций", font=("Arial", 12, "underline")).pack(pady=(10, 5))
        history_frame = ttk.Frame(self.root)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        hist_cols = ("Время", "Операция", "Символ", "Кол-во", "Цена", "Сумма")
        self.history_tree = ttk.Treeview(history_frame, columns=hist_cols, show="headings", height=6)
        for col in hist_cols:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100, anchor="center")
        self.history_tree.pack(fill="both", expand=True)

    def on_market_select(self, event):
        selection = self.market_tree.selection()
        if selection:
            item = self.market_tree.item(selection[0])
            symbol = item["values"][0]
            self.selected_stock = symbol
            stock = self.market.get_stock(symbol)
            if stock:
                self.chart.plot(stock.history, symbol)

    def update_display(self):
        self.balance_label.config(text=f"💵 Наличные: ${self.portfolio.cash:,.2f}")
        total = self.portfolio.get_total_value(self.market)
        self.total_label.config(text=f"📊 Общая стоимость: ${total:,.2f}")

        for item in self.market_tree.get_children():
            self.market_tree.delete(item)
        for stock in self.market.stocks:
            self.market_tree.insert("", "end", values=(stock.symbol, stock.name, f"${stock.price:.2f}"))

        for item in self.portfolio_tree.get_children():
            self.portfolio_tree.delete(item)
        if not self.portfolio.stocks:
            self.portfolio_tree.insert("", "end", values=("", "Портфель пуст", "", ""))
        else:
            for symbol, qty in self.portfolio.stocks.items():
                stock = self.market.get_stock(symbol)
                if stock:
                    value = stock.price * qty
                    self.portfolio_tree.insert("", "end", values=(
                        symbol, qty, f"${stock.price:.2f}", f"${value:.2f}"
                    ))

        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        for op in reversed(self.portfolio.history[-20:]):
            op_type = "Покупка" if op["type"] == "buy" else "Продажа"
            self.history_tree.insert("", "end", values=(
                op["time"],
                op_type,
                op["symbol"],
                op["quantity"],
                f"${op['price']:.2f}",
                f"${op['total']:.2f}"
            ))

        if self.selected_stock:
            stock = self.market.get_stock(self.selected_stock)
            if stock:
                self.chart.plot(stock.history, self.selected_stock)

    def get_inputs(self):
        symbol = self.symbol_entry.get().strip().upper()
        qty_str = self.quantity_entry.get().strip()
        if not symbol:
            messagebox.showwarning("Ошибка", "Введите символ акции.")
            return None, None
        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Количество должно быть целым положительным числом.")
            return None, None
        return symbol, qty

    def buy_stock(self):
        symbol, qty = self.get_inputs()
        if not symbol:
            return
        stock = self.market.get_stock(symbol)
        if not stock:
            messagebox.showerror("Ошибка", f"Акция {symbol} не найдена.")
            return
        if self.portfolio.buy(stock, qty):
            messagebox.showinfo("Успех", f"Куплено {qty} акций {symbol}!")
        else:
            messagebox.showerror("Ошибка", "Недостаточно средств!")
        self.update_display()

    def sell_stock(self):
        symbol, qty = self.get_inputs()
        if not symbol:
            return
        stock = self.market.get_stock(symbol)
        if not stock or self.portfolio.stocks.get(symbol, 0) < qty:
            messagebox.showerror("Ошибка", f"Недостаточно акций {symbol}.")
            return
        if self.portfolio.sell(stock, qty):
            messagebox.showinfo("Успех", f"Продано {qty} акций {symbol}!")
        else:
            messagebox.showerror("Ошибка", "Не удалось продать акции.")
        self.update_display()

    def new_day(self):
        self.market.update_prices()
        messagebox.showinfo("Новый день", "Котировки обновлены!")
        self.update_display()

    def save(self):
        try:
            save_data(self.username, self.portfolio, self.market)
            messagebox.showinfo("Сохранено", "Данные успешно сохранены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")

    def on_closing(self):
        self.save()
        self.root.destroy()

# === ЗАПУСК ===
if __name__ == "__main__":
    username = select_or_create_user()
    root = tk.Tk()
    app = StockApp(root, username)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
