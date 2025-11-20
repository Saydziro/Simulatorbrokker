# models.py
import random
from datetime import datetime
from typing import List, Dict, Optional

class Stock:
    def __init__(self, symbol: str, name: str, price: float, history: List[float] = None):
        self.symbol = symbol
        self.name = name
        self.price = price
        self.history = history or [price]

    def update_price(self):
        change = random.uniform(-0.05, 0.05)
        self.price = round(self.price * (1 + change), 2)
        self.price = max(self.price, 0.01)
        self.history.append(self.price)
        if len(self.history) > 50:
            self.history.pop(0)

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "name": self.name,
            "price": self.price,
            "history": self.history
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["symbol"], data["name"], data["price"], data["history"])


class Portfolio:
    DEFAULT_CASH = 10_000.0

    def __init__(self, cash: float = DEFAULT_CASH, stocks: Dict[str, int] = None, history: list = None):
        self.cash = cash
        self.stocks = stocks or {}
        self.history = history or []

    def buy(self, stock: Stock, qty: int) -> bool:
        cost = stock.price * qty
        if cost > self.cash:
            return False
        self.cash -= cost
        self.stocks[stock.symbol] = self.stocks.get(stock.symbol, 0) + qty
        self.history.append({
            "type": "buy",
            "symbol": stock.symbol,
            "quantity": qty,
            "price": stock.price,
            "total": cost,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        return True

    def sell(self, stock: Stock, qty: int) -> bool:
        owned = self.stocks.get(stock.symbol, 0)
        if qty > owned:
            return False
        income = stock.price * qty
        self.cash += income
        self.stocks[stock.symbol] -= qty
        if self.stocks[stock.symbol] == 0:
            del self.stocks[stock.symbol]
        self.history.append({
            "type": "sell",
            "symbol": stock.symbol,
            "quantity": qty,
            "price": stock.price,
            "total": income,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        return True

    def get_total_value(self, market) -> float:
        value = self.cash
        for symbol, qty in self.stocks.items():
            stock = market.get_stock(symbol)
            if stock:
                value += stock.price * qty
        return value

    def to_dict(self) -> dict:
        return {
            "cash": self.cash,
            "stocks": self.stocks,
            "history": self.history
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["cash"], data["stocks"], data["history"])


class Market:
    DEFAULT_STOCKS = [
        {"symbol": "TECH", "name": "TechNova Inc.", "price": 150.0},
        {"symbol": "ENER", "name": "GreenEnergy Corp.", "price": 85.5},
        {"symbol": "FINX", "name": "Finex Bank", "price": 210.0},
        {"symbol": "RETL", "name": "ShopEasy Stores", "price": 45.25},
        {"symbol": "MEDX", "name": "MediHealth Ltd.", "price": 320.75},
    ]

    def __init__(self, stocks_data: list = None):
        if stocks_data:
            self.stocks = [Stock.from_dict(s) for s in stocks_data]
        else:
            self.stocks = [Stock(s["symbol"], s["name"], s["price"]) for s in self.DEFAULT_STOCKS]

    def get_stock(self, symbol: str) -> Optional[Stock]:
        for s in self.stocks:
            if s.symbol == symbol:
                return s
        return None

    def update_prices(self):
        for s in self.stocks:
            s.update_price()

    def to_dict(self) -> list:
        return [s.to_dict() for s in self.stocks]
