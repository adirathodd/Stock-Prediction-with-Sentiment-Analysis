from sys import argv
from stock import Stock

class Main:
    def __init__(self, ticker):
        self.ticker = ticker
    
    def run(self):
        stock = Stock(self.ticker)
        stock.create(3)
        stock.sentiment_analysis()
        stock.predict()
        stock.print()

main = Main(str(argv[1]))
main.run()