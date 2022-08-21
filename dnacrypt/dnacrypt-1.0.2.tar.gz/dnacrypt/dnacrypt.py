try:
    import random
    status_random = "random package is installed"
except:
    status_random = "random package is NOT installed!\nPlease install this package before use dnacrypt"

try:
    from unidecode import unidecode
    status_unidecode = "unidecode package is installed"
except:
    status_unidecode = "unidecode package is NOT installed!\nPlease install this package before use dnacrypt"

class dnacrypt:

  # Constantes
  start = "AUG"
  stops = ["UAA", "UAG", "UGA"]
  c_cod = {  
      
      'A': 'UUU', 'B': 'UUC', 'C': 'UUA', 'D': 'UUG', 'E': 'UCU', 'F': 'UCC', 
      'G': 'UCA', 'H': 'UCG', 'I': 'UAU', 'J': 'UAC', 'K': 'GCA', 'L': 'UGU', 
      'M': 'UGC', 'N': 'GCG', 'O': 'UGG', 'P': 'CUU', 'Q': 'CUC', 'R': 'CUA', 
      'S': 'CUG', 'T': 'CCU', 'U': 'CCC', 'V': 'CCA', 'W': 'CCG', 'X': 'CAU', 
      'Y': 'CAC', 'Z': 'CAA', 'a': 'CAG', 'b': 'CGU', 'c': 'CGC', 'd': 'CGA', 
      'e': 'CGG', 'f': 'AUU', 'g': 'AUC', 'h': 'AUA', 'i': 'ACU', 'j': 'ACC', 
      'k': 'ACA', 'l': 'ACG', 'm': 'AAU', 'n': 'AAC', 'o': 'AAA', 'p': 'AAG', 
      'q': 'AGU', 'r': 'AGC', 's': 'AGA', 't': 'AGG', 'u': 'GUU', 'v': 'GUC', 
      'w': 'GUA', 'x': 'GUG', 'y': 'GCU', 'z': 'GCC', ' ': 'GAU', '"': 'GAC', 
      '\"': 'GAA', '(': 'GAG', ')': 'GGU', '.': 'GGC', '!': 'GGA', '?': 'GGG',
      '\'': 'XAU'
  }
  
  description = "\033[1mdnacrypt\033[0m is package that uses simple python code without dependencies to encrypt and decrypt a text pass for user into DNA CODE.\nCoder: Forti, R. M.\n\nEnjoy yourself!\n"

  use = "\ndnacrypt('<type>','<msg>')\n\ntype:\nencrypt - \033[1;3mDNA Encryption\033[0m\ndecrypt - \033[1;3mDNA Decryption\033[0m\n\nmsg - \033[1;3mText you want work!\033[0m\n"

  required = "Please install random & unidecode packages to use dnacrypt!\n"


  def __init__(self,type = "",msg = ""):
    self.type = type
    self.msg = msg

    self.out = ""
    
    if self.type == "":
      print("\033[1;31m\033[1mdnacrypt ERROR!\n\033[1;31mtype is NOT defined!!!\033[0m\n\ndnacrypt('\033[1;31m<type>\033[0m','<msg>')")
    elif self.msg == "":
      print("\033[1;31m\033[1mdnacrypt ERROR!\n\033[1;31mmsg is NOT defined!!!\033[0m\n\ndnacrypt('<type>','\033[1;31m<msg>\033[0m')")
    elif self.type == "encrypt":
      #pass
      data = unidecode(self.msg)
      # Converte os codons codificantes em array 
      p_trash = list(self.c_cod.values())
      trash1 = ""
      for x in range(random.randint(1, 59)): 
          trash1 += str(p_trash[x])
      trash2 = ""
      for f in range(random.randint(1, 59)): 
          trash2 += str(p_trash[f])
      converted_data = self.start 
      for i in range(0, len(data)): 
          if data[i] in self.c_cod.keys(): 
              converted_data += self.c_cod[data[i]] 
          else: 
              converted_data += data[i] 
      converted_data += self.stops[random.randrange(len(self.stops))]
      final = trash1 + converted_data + trash2

      self.out = final

    elif self.type == "decrypt":
      #pass
      # list out keys and values separately
      key_list = list(self.c_cod.keys())
      val_list = list(self.c_cod.values())
      
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
      print("\033[1;31m\033[1mdnacrypt ERROR!\n\033[1;31mPlease read how to use this package!!!\033[0m\n",self.use)

    
  def params(self):
    retorno = "Params Passed:\nType: " + self.type + "\nText: " + self.msg
    return retorno

  def status():
    if status_random == "random package is installed" and status_unidecode == "unidecode package is installed":
      retorno = "dnacrypt is ready to use!!!"
      
    else:
      retorno = status_random + "\n" + status_unidecode
      
    return retorno  

  def show(self):
      return self.out  

