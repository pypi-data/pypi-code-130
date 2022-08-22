from cgitb import text
from cryptography.fernet import Fernet

key = Fernet.generate_key()
password = Fernet(key)

class Hello:
    encoded = input("Enter the string you want to encrypt.")
    encoded = bytes(encoded, encoding='utf-8')
    text = password.encrypt(encoded)
    this_line = "\n"
    new_line = bytes(this_line, 'utf-8')

    def encrypting():      

        with open("storing.txt","ab") as file:
            
            file.write(Hello.new_line)   
            file.write(Hello.text)
                 
        return text
    
    def decrypting():
        normal = password.decrypt(Hello.text)
#print(normal)

        with open("decrypted.txt","ab") as f:
            f.write(normal)
Hello.encrypting()
Hello.decrypting()