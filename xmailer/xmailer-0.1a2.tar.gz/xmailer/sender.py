def setup(mail,author=True,debug=False,url="https://h164322.srv12.test-hf.su"):
    self.mail = mail
    self.author = author
    self.url = url
    if debug == True:
        print("Setup mail...")
        print(mail)
        print(f"Author is {str(debug).lower()}")

def send(to,subject,message):
    mail = self.mail
    author = self.author
    url = self.url
    if author == True:
        requests.get(f"{url}/mail.php?to={to}&subject={subject}&message={message}\n\nSended with xmailer! https://walldev.ml/xmailer&from={mail}")
    else:
        requests.get(f"{url}/mail.php?to={to}&subject={subject}&message={message}&from={mail}")
