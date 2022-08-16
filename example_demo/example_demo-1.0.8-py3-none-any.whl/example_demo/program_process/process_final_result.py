from example_demo.monitor.monitor_signal_alert import send_mail
class ResultReportBase:
    def __init__(self, final_result, sour, **kwargs):
        self.final_result = final_result
        self.sour = sour

    def result_process(self):
        email_info = self.sour.get("email_info")
        if email_info:
            self.email_report_process(email_info)

    def email_report_process(self, email_info):
        pass
