import engine


class Stock(object):
    def __init__(self, code):
        self.realtime_url = "https://stock.xueqiu.com/v5/stock/realtime/quotec.json"

        self.code = code
        self.params = {
            "symbol": self.code
        }

        self.eg = engine.Engine()

    def get_realtime_quotec(self):
        txt = self.eg.get_html_text(self.realtime_url, self.params)
        print(txt)


if __name__ == "__main__":
    st = Stock("SH000001")
    st.get_realtime_quotec()
