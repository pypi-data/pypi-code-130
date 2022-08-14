import smtplib
from art import tprint
from email.mime.text import MIMEText

def send_email(message, subject, to, sender="postg.sender@gmail.com",  password="kafobsozsahnlxui", see_prints=False):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    try:
        server.login(sender, password)
        msg = MIMEText(message)
        msg["Subject"] = subject
        server.sendmail(sender, to, msg.as_string())
        if see_prints == True:
              print("\n[INFO]: Connecting...")
              print("-000000000, 10%")
              print("--00000000, 20%")
              print("---0000000, 30%")
              print("----000000, 40%")
              print("-----00000, 50%")
              print("------0000, 60%")
              print("-------000, 70%")
              print("--------00, 80%")
              print("---------0, 90%")
              print("----------, 100%")
        return "[INFO]: Sended!"
    except Exception:
        return "\n[INFO]: Error!"

def main():
    tprint("Post-G")
    print("Install a PostG module: $ pip install postg")
    print("Example:")
    print("\nimport postg")
    print('postg.send_email("Hello!", "My Subject",  "testemail@gmail.com")')
    print("")
    print("[INFO]: use '/exit' for exit")
    print("")
    print("=" * 80)
    while True:
        to = input("\nEnter recipient Email: ")
        if to != "/exit":
            message = input('Enter a message: ')
            if message != "/exit":
                subject = input("Enter a subject of message: ")
                if subject !="/exit":
                    print(send_email(message=message, subject=subject, to=to, see_prints=True), "\n")
                else:
                    break
            else:
                break
        else:
            break
