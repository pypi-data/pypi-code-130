import engine


class Stock(object):
    def __init__(self):
        # Initialize the Stock's constants
        self.realtime_url = "https://stock.xueqiu.com/v5/stock/realtime/quotec.json"

        # Initialize the Stock's variables
        self.params = {

        }

        # Initialize the Engine
        self.eg = engine.Engine()

    def get_realtime_quotec(self, code):  # Get the realtime data of quotec
        self.params["symbol"] = code
        txt = self.eg.get_html_text(self.realtime_url, self.params)     # Use the Engine to get the HTML text.
        print(txt)


if __name__ == "__main__":
    st = Stock()
    st.get_realtime_quotec("SH000001")
