import json
import logging

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
        quotec_json = json.loads(txt)
        # if quotec_json["error_code"] == 0:
        #     logging.info(logging.INFO, "Successfully got the quotec of SH000001")
        # else:
        #     logging.info(logging.ERROR, "Error for getting quotec of SH000001")
        return quotec_json

    def get_realtime_quotec_prize(self, code):
        rt = self.get_realtime_quotec(code)
        if rt["error_code"] == 0:
            return rt["data"][0]["current"]
        else:
            return -1


if __name__ == "__main__":
    st = Stock()
    rt = st.get_realtime_quotec("SH000001")
    print(rt)
    pz = st.get_realtime_quotec_prize("SH000001")
    print(pz)
