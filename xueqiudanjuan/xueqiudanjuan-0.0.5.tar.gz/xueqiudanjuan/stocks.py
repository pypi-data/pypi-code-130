import engine


class Stock(object):
    def __init__(self, code):
        # Initialize the Stock' constants
        self.realtime_url = "https://stock.xueqiu.com/v5/stock/realtime/quotec.json"

        # Initialize the Stock's variables
        self.code = code
        self.params = {
            "symbol": self.code
        }

        # Initialize the Engine
        self.eg = engine.Engine()

    def get_realtime_quotec(self):  # Get the realtime data of quotec
        txt = self.eg.get_html_text(self.realtime_url, self.params) # Use the Engine to get the HTML text or the json string.
        print(txt)


if __name__ == "__main__":
    st = Stock("SH000001")
    st.get_realtime_quotec()
