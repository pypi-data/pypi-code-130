from requests.structures import CaseInsensitiveDict
from requests import post

class Firebase:
    def send_notifications(sender,receiver,title,body):
        url = "https://fcm.googleapis.com/fcm/send"

        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers[
            "Authorization"] = "key=AAAAu_exkBc:APA91bGmfBXXUMRHaGVdhNGlmazAQ8WrjvJAFMRhJTD3Lo-61avhPS0EKxUokq08hW0k-w2Gi-mGrUL-C7qr6YdQihqLSMY_xB_W9L9g0w6LjkOg9HptxIKzRuEPdWtmCsCGYIAxQUh6"
        headers["Content-Type"] = "application/json"
        to = "\"" + str(receiver.user_id.noti_token) + "\""
        data = """
                    {
                        "to": """ + to + """,
                        "notification": {
                            "title": """+title+""",
                            "body":""" + body + """
                        }
                    }
                    """

        resp = post(url, headers=headers, data=data)
        return resp

firebase = Firebase()
send_notifications=Firebase.send_notifications()
