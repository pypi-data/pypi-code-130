try:
    import random
    status_random = "random package is installed"
except:
    status_random = "random package is NOT installed!\nPlease install this package before use dnacryptkey"

try:
    from unidecode import unidecode
    status_unidecode = "unidecode package is installed"
except:
    status_unidecode = "unidecode package is NOT installed!\nPlease install this package before use dnacryptkey"

class dnacryptkey:

  # Constantes
  start = "AUG"
  stops = ["UAA", "UAG", "UGA"]

  description = "\033[1mdnacryptkey\033[0m is package that uses simple python code without dependencies to encrypt and decrypt a text pass for user into DNA CODE.\nCoder: Forti, R. M.\n\nEnjoy yourself!\n"

  use = "\ndnacryptkey('<type>','<msg>','<key>')\n\ntype:\nencrypt - \033[1;3mDNA Encryption\033[0m\ndecrypt - \033[1;3mDNA Decryption\033[0m\n\nmsg - \033[1;3mText you want work!\033[0m\n\nkey - \033[1;3mSecret Key\033[0m\n"

  required = "Please install random & unidecode packages to use dnacryptkey!\n"


  def __init__(self,type = "",msg = "", key = ""):
    self.type = type
    self.msg = msg
    self.key = key

    self.keys = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',' ','"','(',')','.','!','?','\'','@','$','_','-','#','/','&','%','£','*','§',',',':',';','=','0','1','2','3','4','5','6','7','8','9','|','\\','[',']']   
    
    self.values = ['UUU','UUC','UUA','UUG','UCU','UCC','UCA','UCG','UAU','UAC','GCA','UGU','UGC','GCG','UGG','CUU','CUC','CUA','CUG','CCU','CCC','CCA','CCG','CAU','CAC','CAA','CAG','CGU','CGC','CGA','CGG','AUU','AUC','AUA','ACU','ACC','ACA','ACG','AAU','AAC','AAA','AAG','AGU','AGC','AGA','AGG','GUU','GUC','GUA','GUG','GCU','GCC','GAU','GAC','GAA','GAG','GGU','GGC','GGA','GGG','TAA','TAG','TAT','TAC','TTT','TGT','TCT','TGG','ATA','ATT','ATC','ATG','AGT','GTT','GTA','GTC','GGT','GAT','CCT','CTC','CTG','CAT','CGT','TUC','TTU','TCU','TGU','TUT','UTT']
    
    charData = self.key
    soma = 0
    for x in charData:
      soma = soma + ord(x)
    
    s2 = 0
    for somai in str(soma):
      s2 = s2 + int(somai)
    
    div = soma%64
    
    FINAL = div + s2
    if FINAL > 89:
      FINAL = FINAL%10
    
    self.res = {}
    cln = len(self.keys)
    start = FINAL
    i = 0
    while i < cln:
        pos = i+start
        for value in self.values:
            self.res[self.keys[pos if pos<cln else pos-cln]] = value
            self.values.remove(value)
            break 
        i += 1
        
    self.out = ""
    
    if self.type == "":
      print("\033[1;31m\033[1mdnacryptkey ERROR!\n\033[1;31mtype is NOT defined!!!\033[0m\n\ndnacryptkey('\033[1;31m<type>\033[0m','<msg>','<key>')")
    elif self.msg == "":
      print("\033[1;31m\033[1mdnacryptkey ERROR!\n\033[1;31mmsg is NOT defined!!!\033[0m\n\ndnacryptkey('<type>','\033[1;31m<msg>\033[0m','<key>')")
    elif self.key == "":
      print("\033[1;31m\033[1mdnacryptkey ERROR!\n\033[1;31mkey is NOT defined!!!\033[0m\n\ndnacryptkey('<type>','<msg>','\033[1;31m<key>\033[0m')")  
    elif self.type == "encrypt":
      #pass
      data = unidecode(self.msg)
      # Converte os codons codificantes em array 
      p_trash = list(self.res.values())
      trash1 = ""
      for x in range(random.randint(1, 59)): 
          trash1 += str(p_trash[x])
      trash2 = ""
      for f in range(random.randint(1, 59)): 
          trash2 += str(p_trash[f])
      converted_data = self.start 
      for i in range(0, len(data)): 
          if data[i] in self.res.keys(): 
              converted_data += self.res[data[i]] 
          else: 
              converted_data += data[i] 
      converted_data += self.stops[random.randrange(len(self.stops))]
      final = trash1 + converted_data + trash2

      self.out = final

    elif self.type == "decrypt":
      #pass
      # list out keys and values separately
      key_list = list(self.res.keys())
      val_list = list(self.res.values())
      
      fator = 3
      num_codons = len(self.msg)/fator
      msg = ""
      traduzindo = "NAO"
      codons = [self.msg[i:i+fator] for i in range(0, len(self.msg), fator)]
      for i in codons:
        if i == self.start:
          traduzindo = "SIM"
        elif i in self.stops:
          traduzindo = "NAO"
    
        if traduzindo == "SIM":
          if i != "AUG":
            position = val_list.index(i)
            msg += key_list[position]
    
      self.out = msg

      
    else:
      print("\033[1;31m\033[1mdnacryptkey ERROR!\n\033[1;31mPlease read how to use this package!!!\033[0m\n",self.use)

    
  def params(self):
    retorno = "Params Passed:\nType: " + self.type + "\nText: " + self.msg + "\nKey: " + self.key
    return retorno

  def status():
    if status_random == "random package is installed" and status_unidecode == "unidecode package is installed":
      retorno = "dnacryptkey is ready to use!!!"
      
    else:
      retorno = status_random + "\n" + status_unidecode
      
    return retorno  

  def show(self):
      return self.out  

