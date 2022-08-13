import random

 #Символы
sSym = '&$%@=¿!qwertyuiopasdfghjklzxcvbnm1234567890'

# Шифровка
def enscrypt(text):
    
    tx = ''

    for i in text:
        
        # Если символ цифра
        if i.isdigit() == True:
            eSym = random.choice(sSym)
            tx += f'nS+{ord(i)}{eSym}S%$'
        
        # Если символ буква
        elif i.isdigit() == False and i != ' ':
            Lsym = random.randint(0,1)
            if Lsym == 0:
                Lsym = 'l'
            elif Lsym == 1:
                Lsym = 'L'
            Sym2 = random.choice(sSym)
            Sym3 = random.choice(sSym)
            
            tx += f'{Lsym}{Sym2}={Sym3}{ord(i)}S%$'
        
        # Если символ пробел
        elif i.isdigit() == False and i == ' ':
            Ssym = random.randint(0,1)
            if Ssym == 0:
                Ssym = 's'
            elif Ssym == 1:
                Ssym = 'S'
            Sym2 = random.choice(sSym)
            Sym3 = random.choice(sSym)
                    
            tx += f'{Ssym}{Sym2}={Sym3}{ord(i)}S%$'
    
    tx = tx[0:-3]
    return tx

# Расшифровка
def decrypt(text):

    tx = ''
    
    get = text.split('S%$')
    
    for i in get:
        
        # Если символ цифра
        if i[0:3] == 'nS+' and i[-1] in sSym:
            tx += f'{chr(int(i[3:-1]))}'
                
        # Если символ буква
        elif i[0].lower() == 'l' and i[2] == '=' and i[3] in sSym and i[1] in sSym:
            tx += f'{chr(int(i[4:-1] + i[-1]))}'
        
        # Если символ пробел
        elif i[0].lower() == 's' and i[2] == '=' and i[3] in sSym and i[1] in sSym:
            tx += f'{chr(int(i[4:-1] + i[-1]))}'
    
    return tx