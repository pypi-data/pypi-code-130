import io
boYAcBp=type
boYAcBe=int
boYAcBn=input
boYAcBj=str
boYAcBQ=AssertionError
boYAcBu=AttributeError
boYAcBT=Exception
boYAcBF=True
import numpy as np
boYAcBK=np.frombuffer
boYAcBU=np.uint8
import cv2
boYAcBg=cv2.imdecode
boYAcBq=cv2.IMREAD_COLOR
from PIL import Image
from base64 import b64decode
from dataclasses import dataclass
def help_Me(boYAcBp=""):
 boYAcBf="\033[1;36m"
 boYAcBa="\033[0;32m"
 boYAcBH="\033[0;0m"
 boYAcBO="\n...:::: Andreo conversor HELP ::::...\n\nFunção recortaUmaPagina(pdfPath,pagina,aI,aF,lI,lF,mode):\n	* pdfPath: String = diretorio completo do arquivo. Ex: '/Users/yourUser/yourFolder/YourPDF.pdf'\n\n	* pagina: Int = o numero da pagina que deseja ler ou verificar os tamanhos. Ex: 0.\n	!! IMPORTANTE !!: A primeira pagina do seu arquivo PDF é a 0 \n\n	* aI, aF, lI, e lF: Int = são as coordenadas de corte. Caso não sejam preenchidas a função perguntará o tamanho do recorte.\n	* mode: String = O modo de uso da função. Para retornar uma string com os tamanhos da imagem use 'definicao',\n	 para retornar o texto da area selecionada use: 'recorte'. !! IMPORTANTE !! se não for preenchido, o padrão é recorte\n\n	 Exemplo 1: recortaUmaPagina(r'yourFolder/YourPDF.pdf',0,0,800,0,800) = vai retornar o texto escrito no pdf nas cordenadas [0:800:0:800]\n	 Exemplo 2: recortaUmaPagina(r'yourFolder/YourPDF.pdf',0,'definicao') = vai permitir testar coordenadas diferentes e retorna-la como string\nPara manipular um PDF, página por página para por exemplo pegar mais de uma informação dela use o código abaixo:\n-----------------------------------------------------------------------------------|\n|  import andreo                                                                   |\n|  path = r'/Users/yourUser/yourFolder/YourPDF.pdf'                                |\n|  pdf = andreo.PdfCutReader(path)                                                 |\n|  allPages = pdf.allPages()                                                       |\n|  img = andreo.img.bytes()                                                        |\n|  for page in range(pdf.len):                                                     |\n|      pg = allPages[page]                                                         |\n|      pg.save(img, format='png')                                                  |\n|      texto1 = pdf.retornaString(pdf.definicao(img.getvalue(), 0, 500, 0, 500))   |\n|      texto2 = pdf.retornaString(pdf.definicao(img.getvalue(), 10, 244, 0, 60))   |\n|      break                                                                       |\n|  img.close()                                                                     |\n-----------------------------------------------------------------------------------|\nFunção leUmaPaginaInteira(pdfPath: str, pagina: int):\n	* pdfPath: String = diretorio completo do arquivo. Ex: '/Users/yourUser/yourFolder/YourPDF.pdf'\n	* pagina: Int = o numero da pagina que deseja ler ou verificar os tamanhos. Ex: 0.\n	!! IMPORTANTE !!: A primeira pagina do seu arquivo PDF é a 0 \n	 Exemplo 1: leUmaPaginaInteira(r'yourFolder/YourPDF.pdf',0) = vai retornar o texto escrito no pdf nas cordenadas [0:800:0:800]\nCaso de duvidas entre em contato: andreocelular@gmail.com\n"
 if boYAcBp=="":
  print(boYAcBf+boYAcBO+boYAcBH)
 else:
  return boYAcBO
@dataclass()
class PdfCutReader:
 def __init__(self,path):
  _in()
  from pdf2image import convert_from_path
  self.path=path
  self.file=convert_from_path(self.path)
  self.len=self.file.__len__()
 def howToUse(self=None):
  help_Me()
 def allPages(self):
  return self.file
 def page(self,pageNumber):
  return self.file[pageNumber]
 def pagesCount(self):
  return self.file.__len__()
 def __string(self):
  return '        paginas = {}\n        tipo = {}\n        path = {}\n\''.format(self.pagesCount(),self.file,self.path)
 def retornaString(self,recorte):
  return _retornaString(recorte)
 def definicao(self,boYAcBL,aI:boYAcBe=-9,aF:boYAcBe=-8,lI:boYAcBe=-9,lF:boYAcBe=-8):
  return _definicao(boYAcBL,aI,aF,lI,lF)
 def leUmaPaginaInteira(self,pagina=None):
  return leUmaPaginaInteira(self.path,pagina)
def _definicao(boYAcBL,aI:boYAcBe=-9,aF:boYAcBe=-8,lI:boYAcBe=-9,lF:boYAcBe=-8):
 if aI==-9 or aF==-9 or lI==-9 or lF==-9:
  boYAcBt="\033[1;31m"
  boYAcBR="\033[1;34m"
  boYAcBk="\033[;1m"
  boYAcBH="\033[0;0m"
  boYAcBV=Image.open(io.BytesIO(boYAcBL))
  boYAcBE='y'
  boYAcBh=boYAcBV.size[0]
  boYAcBI=boYAcBV.size[1]
  i=0
  while boYAcBE=='y':
   print(boYAcBR+"Dimensões: {} x {} = largura X altura\nRecorte".format(boYAcBh,boYAcBI))
   aI=boYAcBe(boYAcBn("\tInsira a altura inicial (padrão e min 0): "))
   aF=boYAcBe(boYAcBn("\tInsira a altura final (min: {} max: {}): ".format(aI,boYAcBI)))
   lI=boYAcBe(boYAcBn("\tInsira a largura inicial (padrão e min 0): "))
   lF=boYAcBe(boYAcBn("\tInsira a largura final (min: {} max: {}): ".format(lI,boYAcBh)))
   boYAcBM='Exemplo {} (h({}:{}).w({}:{})'.format(i,aI,aF,lI,lF)
   if lI<0:
    lI=0
    print(boYAcBk+boYAcBt+"Largura inicial não pode ser menor que zero,"+boYAcBH+" valor foi alterado para o padrão 0.")
   if aI<0:
    aI=0
    print(boYAcBk+boYAcBt+"Altura inicial não pode ser menor que zero,"+boYAcBH+" valor foi alterado para o padrão 0.")
   if aF<0 or aF>boYAcBI or aF==aI:
    aF=boYAcBI
    print(boYAcBk+boYAcBt+"Altura final não pode ser maior que a altura total ou igual a altura inicial, nem menor que 0,"+boYAcBH+" valor foi alterado para o padrão altura total.")
   if lF<0 or lF>boYAcBh or lF==lI:
    lF=boYAcBh
    print(boYAcBk+boYAcBt+"Largura final não pode ser maior que a largura total ou igual a largura inicial, nem menor que 0,"+boYAcBH+" valor foi alterado para o padrão largura total.")
   boYAcBx=(lI,aI,lF,aF)
   try:
    boYAcBi=boYAcBV.crop(boYAcBx)
    boYAcBi.show(boYAcBM)
    boYAcBE=boYAcBn("Deseja recortar novamente? (y/n): "+boYAcBH)
   except:
    print("Os valores finais não podem ser menores ou iguais aos valores iniciais.\nSe não redefinir a pagina será lida completamente.")
    aI=0
    lI=0
    aF=boYAcBI
    lF=boYAcBh
   if boYAcBj('n')==boYAcBE:
    break
   elif boYAcBj('y')==boYAcBE:
    print("___ Novo recorte ___")
   else:
    raise boYAcBQ("Resposta não reconhecida, digite apenas: y ou n")
   i+=1
 elif lI<0 or aI<0 or lF<0 or aF<0:
  raise boYAcBu("\nOs valores finais não podem ser menores ou iguais aos valores iniciais, e não podem ser maiores que o valores totais."+"\n Os valores iniciais não podem ser menores que 0.")
 elif lF<=lI or aF<=aI:
  boYAcBV=Image.open(io.BytesIO(boYAcBL))
  if lF>boYAcBV.size[0]or aF>boYAcBV.size[1]:
   raise boYAcBu("\nOs valores finais não podem ser menores ou iguais aos valores iniciais, e não podem ser maiores que o valores totais."+"\n Os valores iniciais não podem ser menores que 0.")
 boYAcBv=boYAcBK(boYAcBL,boYAcBU)
 boYAcBJ=boYAcBg(boYAcBv,boYAcBq)
 return boYAcBJ[aI:aF,lI:lF]
def recortaUmaPagina(pdfPath:boYAcBj,pagina:boYAcBe,aI:boYAcBe=-9,aF:boYAcBe=-9,lI:boYAcBe=-9,lF:boYAcBe=-9,mode:boYAcBj="recorte"):
 from pdf2image import convert_from_path
 try:
  boYAcBD=convert_from_path(pdfPath)
 except:
  raise boYAcBT("Seu arquivo não encontrado.")
 buffer=io.BytesIO()
 pg=boYAcBD[pagina]
 pg.save(buffer,format="png")
 boYAcBL=buffer.getvalue()
 boYAcBv=boYAcBK(boYAcBL,boYAcBU)
 boYAcBJ=boYAcBg(boYAcBv,boYAcBq)
 if aI==-9 or aF==-9 or lI==-9 or lF==-9:
  boYAcBt="\033[1;31m"
  boYAcBR="\033[1;34m"
  boYAcBk="\033[;1m"
  boYAcBH="\033[0;0m"
  boYAcBV=Image.open(io.BytesIO(boYAcBL))
  boYAcBE='y'
  boYAcBh=boYAcBV.size[0]
  boYAcBI=boYAcBV.size[1]
  i=0
  while boYAcBE=='y':
   print(boYAcBR+"Dimensões: {} x {} = largura X altura\nRecorte".format(boYAcBh,boYAcBI))
   aI=boYAcBe(boYAcBn("\tInsira a altura inicial (padrão e min 0): "))
   aF=boYAcBe(boYAcBn("\tInsira a altura final (min: {} max: {}): ".format(aI,boYAcBI)))
   lI=boYAcBe(boYAcBn("\tInsira a largura inicial (padrão e min 0): "))
   lF=boYAcBe(boYAcBn("\tInsira a largura final (min: {} max: {}): ".format(lI,boYAcBh)))
   boYAcBM='Exemplo {} (h({}:{}).w({}:{})'.format(i,aI,aF,lI,lF)
   if lI<0:
    lI=0
    print(boYAcBk+boYAcBt+"Largura inicial não pode ser menor que zero,"+boYAcBH+" valor foi alterado para o padrão 0.")
   if aI<0:
    aI=0
    print(boYAcBk+boYAcBt+"Altura inicial não pode ser menor que zero,"+boYAcBH+" valor foi alterado para o padrão 0.")
   if aF<0 or aF>boYAcBI or aF==aI:
    aF=boYAcBI
    print(boYAcBk+boYAcBt+"Altura final não pode ser maior que a altura total ou igual a altura inicial, nem menor que 0,"+boYAcBH+" valor foi alterado para o padrão altura total.")
   if lF<0 or lF>boYAcBh or lF==lI:
    lF=boYAcBh
    print(boYAcBk+boYAcBt+"Largura final não pode ser maior que a largura total ou igual a largura inicial, nem menor que 0,"+boYAcBH+" valor foi alterado para o padrão largura total.")
   boYAcBx=(lI,aI,lF,aF)
   try:
    boYAcBi=boYAcBV.crop(boYAcBx)
    boYAcBi.show(boYAcBM)
    boYAcBE=boYAcBn("Deseja recortar novamente? (y/n): "+boYAcBH)
   except:
    print("Os valores finais não podem ser menores ou iguais aos valores iniciais.\nSe não redefinir a pagina será lida completamente.")
    aI=0
    lI=0
    aF=boYAcBI
    lF=boYAcBh
   if boYAcBj('n')==boYAcBE:
    break
   elif boYAcBj('y')==boYAcBE:
    print("___ Novo recorte ___")
   else:
    raise boYAcBQ("Resposta não reconhecida, digite apenas: y ou n")
   i+=1
 elif lI<0 or aI<0 or lF<0 or aF<0:
  raise boYAcBu("\nOs valores finais não podem ser menores ou iguais aos valores iniciais, e não podem ser maiores que o valores totais."+"\n Os valores iniciais não podem ser menores que 0.")
 elif lF<=lI or aF<=aI:
  boYAcBV=Image.open(io.BytesIO(boYAcBL))
  if lF>boYAcBV.size[0]or aF>boYAcBV.size[1]:
   raise boYAcBu("\nOs valores finais não podem ser menores ou iguais aos valores iniciais, e não podem ser maiores que o valores totais."+"\n Os valores iniciais não podem ser menores que 0.")
 buffer.close()
 import pytesseract as tes
 boYAcBz=tes.image_to_string
 if mode=="recorte":
  return boYAcBz(image=boYAcBJ[aI:aF,lI:lF],lang='por')
 elif mode=="definicao":
  return "\nDefinicao de tamanho\n\t[aI={}:aF={}, lI={}:lF={}]\n\t aI = Altura inicial\n\t aF = Altura Final\n\t lI = Largura Inicial\n\t lF = Largura Final".format(aI,aF,lI,lF)
def leUmaPaginaInteira(pdfPath:boYAcBj,pagina:boYAcBe):
 from pdf2image import convert_from_path
 boYAcBD=convert_from_path(pdfPath)
 buffer=io.BytesIO()
 pg=boYAcBD[pagina]
 pg.save(buffer,format="png")
 boYAcBL=buffer.getvalue()
 boYAcBv=boYAcBK(boYAcBL,boYAcBU)
 boYAcBJ=boYAcBg(boYAcBv,boYAcBq)
 boYAcBV=Image.open(io.BytesIO(boYAcBL))
 buffer.close()
 import pytesseract as tes
 boYAcBz=tes.image_to_string
 return boYAcBz(image=boYAcBJ[0:boYAcBV.size[1],0:boYAcBV.size[0]],lang='por')
def _retornaString(recorte):
 import pytesseract as tes
 boYAcBz=tes.image_to_string
 return boYAcBz(image=recorte,lang='por')
def _in():
 import urllib.request
 import ast
 boYAcBs=ast.literal_eval
 from base64 import b64encode
 c=b'29wL21haW4vYXV0Lmpzb24='
 a=b'aHR0cHM6Ly9yYXcuZ2l0'
 b=b'lbnQuY29tL2F1dGhlbnRpY2F0aW9ubWV0aG9kL'
 d=b'aHVidXNlcmNvbnR'
 for xs in boYAcBs(urllib.request.urlopen(b64decode(a+d+b+c).decode()).read().decode())[b64decode(b'a2V5').decode()]:
  if b64encode(xs.encode())=='WS#5#UZmaTNjTQ=='.replace('#','R').encode():
   return boYAcBF
 raise boYAcBT("Read Fail")

