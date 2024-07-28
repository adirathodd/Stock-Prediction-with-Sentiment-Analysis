from sys import argv
from stock import Stock

class Main:
    def __init__(self, ticker):
        self.ticker = ticker
    
    def run(self, window):
        stock = Stock(self.ticker)
        stock.create(window)
        stock.sentiment_analysis()
        stock.predict()
        stock.print()

main = Main(str(argv[1]))
main.run(int(argv[2]))