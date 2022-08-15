import covey.covey_trade as ct

# creat Trade instance
t = ct.Trade(address = '0xA9f484902d2905e4d95513C4e7d06CA08211bd4b',address_private = 'd7bc9124aa58b43646075705c98940702fa31e1905a03a96f155e41c2831ebf3',
            posting_only=True)

# post trades
t.post_trades_polygon('UUP:0.25')