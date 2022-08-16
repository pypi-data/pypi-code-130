from example_demo.monitor.monitor_signal_alert import send_mail


class ResultReportBase:
    def __init__(self, final_result, data_source, **kwargs):
        self.final_result = final_result
        self.data_source = data_source

    def result_process(self):
        email_info = self.data_source.get("email_info")
        if email_info:
            self.email_report_process(email_info)

    def get_email_sub_content(self):
        '''
        return subject , content
        '''
        subject = ''
        content = ''

        return subject, content

    def email_report_process(self, email_info):
        subject,content = self.get_email_sub_content()
        if subject and content:
            send_mail(subject,content,**email_info)
