import requests


class Webhook:
    def __init__(self: object, webhook_url: str, username = None, avatar_url = None):
        self.username = username
        self.avatar = avatar_url
        if requests.get(webhook_url).status_code < 300:
            self.webhook_url = webhook_url
        else: raise Exception("Please provide a **valid webhook url...")
    
    def send(self, content: str):
        if self.username:
            data = {"content": content, "username": self.username}
        elif self.avatar and not self.username:
            data = {"content": content, "avatar_url": self.avatar}
        elif self.avatar and self.username:
            data = {"content": content, "avatar_url": self.avatar, "username": self.username}
        try:
            requests.post(
                url=self.webhook_url,
                json=data
            )
        except Exception as ex:
            raise Exception(ex)
    
    def send_file(self, file_path: str, file_name: str):
        try:
            requests.post(
                url=self.webhook_url,
                files={file_name: open(file_path, "rb").read()}
            )
        except Exception as ex:
            raise Exception(ex)
    
    def change_username(self, username: str):
        self.username = username
    
    def change_avatar(self, avatar_url: str):
        self.avatar = avatar_url
    
    