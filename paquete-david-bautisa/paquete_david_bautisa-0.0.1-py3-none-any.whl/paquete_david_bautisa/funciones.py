class Estadisticos:
    def __init__(self,lista:list):
        self.lista = lista
        self.n = len(self.lista)

    def media(self):
        return sum(self.lista) / len(self.lista)

    def varianza(self):
        return sum([(x - self.media())**2 for x in self.lista]) / (self.n - 1)

    def desviacion(self):
        return self.varianza()**0.5



