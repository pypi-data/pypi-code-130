from backtrader import Strategy
from .azt_store import AztStore
from .azt_ve_wrapper.azt_ve_init import AztVe


class AztStrategy(Strategy):
    # def _start(self):
    #     self.broker.startdatas()
    #     super(AztStrategy, self)._start()

    def start(self):
        pass

    def prenext(self):
        pass

    def next(self):
        pass

    # def _stop(self):
    #     self.broker.stopdatas()
    #     super(AztStrategy, self)._stop()

    def stop(self):
        pass

    def notify_store(self, msg, *args, **kwargs):
        msg_level = msg
        msg_type = args[0]
        msg = args[1]

        if msg_type == AztStore.type_exchange:  # 柜台服务连接中断
            if msg_level == AztStore.level_log:
                AztVe.log(msg)
            elif msg_level == AztStore.level_warning:
                AztVe.warning(msg)
            elif msg_level == AztStore.level_error:
                AztVe.error(msg)
        elif msg_type == AztStore.type_quote:  # 行情服务连接中断
            AztVe.error(msg)

        elif msg_type == AztStore.type_cancelfailed:  # 撤单失败回报
            cancel_req = args[2]
            AztVe.warning(msg, cancel_req)

    def notify_data(self, data, status, *args, **kwargs):
        dataname = data.code
        if status == data.CONNBROKEN:
            AztVe.warning(f"{dataname}订阅通道已失效，需要重新连接行情服务并重新订阅！")
        elif status == data.LIVE:
            msg = args[0]
            AztVe.log(f"获取{dataname}订阅回复消息：{msg}")
