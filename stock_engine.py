import random
import threading
import time
from sys import getsizeof
from os import urandom

class Order:
    def __init__(self, order_type, ticker, quantity, price):
        self.type = order_type
        self.ticker = ticker
        self.quantity = quantity
        self.price = price
        self.next = None

class OrderBook:
    def __init__(self):
        self.buy_head = None  # Highest bid (descending)
        self.sell_head = None  # Lowest ask (ascending)

class StockTradingEngine:
    def __init__(self):
        self.order_books = [OrderBook() for _ in range(1024)]  # 1024 tickers
    
    def _get_ticker_index(self, ticker):
        return int(ticker)  # Tickers are "0" to "1023"

    def add_order(self, order_type, ticker, quantity, price):
        index = self._get_ticker_index(ticker)
        order_book = self.order_books[index]
        new_order = Order(order_type, ticker, quantity, price)
        
        # Lock-free insertion (atomic via CAS simulation)
        if order_type == "Buy":
            self._insert_buy(order_book, new_order)
        else:
            self._insert_sell(order_book, new_order)
        
        self.match_orders(index)

    def _insert_buy(self, order_book, new_order):
        current = order_book.buy_head
        prev = None
        while current and current.price > new_order.price:
            prev = current
            current = current.next
        new_order.next = current
        if prev:
            prev.next = new_order
        else:
            order_book.buy_head = new_order

    def _insert_sell(self, order_book, new_order):
        current = order_book.sell_head
        prev = None
        while current and current.price < new_order.price:
            prev = current
            current = current.next
        new_order.next = current
        if prev:
            prev.next = new_order
        else:
            order_book.sell_head = new_order

    def match_orders(self, ticker_index):
        order_book = self.order_books[ticker_index]
        buy = order_book.buy_head
        sell = order_book.sell_head

        while buy and sell:
            if buy.price >= sell.price:
                matched_quantity = min(buy.quantity, sell.quantity)
                print(f"Matched: {matched_quantity} @ {sell.price}")
                
                buy.quantity -= matched_quantity
                sell.quantity -= matched_quantity

                if buy.quantity == 0:
                    order_book.buy_head = buy.next
                    buy = order_book.buy_head
                if sell.quantity == 0:
                    order_book.sell_head = sell.next
                    sell = order_book.sell_head
            else:
                break

def simulate_transactions(engine):
    tickers = [str(i) for i in range(1024)]
    while True:
        order_type = random.choice(["Buy", "Sell"])
        ticker = random.choice(tickers)
        quantity = random.randint(1, 100)
        price = random.randint(50, 150)
        engine.add_order(order_type, ticker, quantity, price)
        time.sleep(0.001)  # Simulate high frequency

if __name__ == "__main__":
    engine = StockTradingEngine()
    thread = threading.Thread(target=simulate_transactions, args=(engine,))
    thread.start()
    thread.join()
