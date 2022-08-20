# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

class SehirNesnesi:
    def __repr__(self) -> str:
        return f"{__class__.__name__}({self.__sozluk})"

    def __init__(self, sozluk:dict):
        self.__sozluk = sozluk

        assert isinstance(self.__sozluk, dict)
        for key, value in self.__sozluk.items():
            if isinstance(value, (list, tuple)):
                setattr(self, key, [SehirNesnesi(veri) if isinstance(veri, dict) else veri for veri in value])
            else:
                setattr(self, key, SehirNesnesi(value) if isinstance(value, dict) else value)

from TRSehirler.Sehirler import Sehir