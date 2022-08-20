import json
import os
import typing

import aiofiles
import aiohttp
from aiohttp import FormData


class Client:
    def __init__(self, token: str, download_path: str = "korrektor_docs"):
        self._token = token
        self.download_path = download_path
        self.base_url = "https://korrektor.uz/api"

    @property
    def headers(self):
        return {'Authorization': "Bearer " + self._token}

    @property
    def headers_json(self):
        return {"Authorization": "Bearer " + self._token, "Content-type": "application/json"}

    async def info(self):
        """give information about this class, its methods and its attributes"""
        msg = """
        Korrektor API class.
        Methods:
         * spell_check(words: list, remove_identifiers: bool = False)
         * transliterate(text: str, alphabet: str ['cyrillic' | 'latin'])
         * auto_correct(text: str)
         * rem_modifiers(text: str)
         * tokenize(text: str)
         * num2words(num: int)
         * word_frequency(text: str)
         * remove_duplicates(text: str)
         * alphabet_sorting(text: str)
         * ocr(image: str)
         * doc(doc: str, alphabet: str ['cyrillic' | 'latin'])
        
        Attributes:
         * token: str => token for authorization
         * download_path: str => path for downloading documents
        
        Usage:
        korrektor = Client(token=<token>)
        response = await korrektor.spell_check(words=['salom', "dunyo"])
        response = await korrektor.spell_check(words=['saloma', "dunyo"], remove_identifiers=True)
        ... etc ...
        
        Detailed information is on https://korrektor.uz/api
        """
        return msg

    async def _send_request(self, endpoint: str, data: typing.Any, **kwargs) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url + endpoint,
                                    headers=self.headers,
                                    data=data
                                    ) as response:
                return await response.json()

    async def _send_document(self, endpoint: str, data: typing.Any, **kwargs) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url + endpoint,
                                    headers=self.headers,
                                    data=data
                                    ) as response:
                if response.content_type == "application/json":
                    return await response.json()
                else:
                    filename = response.headers["Content-Disposition"].split("filename=")[1].replace(";", "")
                    if not os.path.exists(self.download_path):
                        os.mkdir(self.download_path)
                    async with aiofiles.open(self.download_path + "/" + filename, "wb") as f:
                        await f.write(await response.read())
                return {"status": "successful", "code": 200, "description": "Successful",
                        "filename": self.download_path + "/" + filename}

    async def spell_check(self, words: list, remove_identifiers: bool = False) -> dict:
        """
        :param words: list =>  Tekshirish uchun so’zlar massivi
        :param remove_identifiers:  bool => So’zlarni tekshirish jarayonida yuklamalarni tozalash. Misol uchun
bormoqda-ku so’zi uchun bormoqda so’zi qabul qilinadi
        :return: dict

        Usage:
        korrektor = Client(token=<token>)
        response = await korrektor.spell_check(words=['salom', "dunyo"])
        response = await korrektor.spell_check(words=['saloma', "dunyo"], remove_identifiers=True)


        """
        if not words:
            return {"status": "unsuccessful",
                    "code": 0,
                    "description": "Foydalanish uchun so'zlar listini words ga yozing"}
        data = json.dumps({"words": words, "remove_identifiers": remove_identifiers})
        response = await self._send_request(endpoint="/spellCheck",
                                            data=data)
        return response

    async def transliterate(self, text: str, alphabet: str) -> dict:
        """
        :param alphabet: str ['cyrillic' | 'latin'] =>  Matnni qaysi alifboga o’girish
        :param text: str => Transliteratsiya qilish uchun matn
        :return: dict

        Usage: 
        korrektor = Client(token=<token>)
        response = await korrektor.transliterate(text="Salom, dunyo", alphabet="cyrillic")
        yoki
        response = await korrektor.transliterate("Салом, Дунё", "latin")
        """
        if not alphabet or not text:
            return {"status": "unsuccessful",
                    "code": 2,
                    "description": "metoddan foydalanish uchun *text* va *alphabet* parameterlarini to'ldiring!"}
        data = FormData()
        data.add_field(
            name='text',
            value=text
        )
        data.add_field(
            name="alphabet",
            value=alphabet
        )

        response = await self._send_request(endpoint="/transliterate", data=data)
        return response

    async def auto_correct(self, text: str) -> dict:
        """
        :param text: str => Majburiy. Korreksiya qilish uchun matn
        :return: dict

        Usage:
        korrektor = Client(token=<token>)
        response = await korrektor.auto_correct("O'zbekcha matn")
        """
        if not text:
            return {
                "status": "unsuccessful",
                "code": 3,
                "description": "Foydalanish uchun \n\tkorrektor = Client(token=<token>)\n"
                               "\tresponse = await korrektor.auto_correct(\"O'zbekcha matn\")"
            }
        data = FormData()
        data.add_field(name="text", value=text)
        response = await self._send_request(endpoint="/autoCorrect", data=data)
        return response

    async def rem_modifiers(self, text: str) -> dict:
        """
        :param text: str => Majburiy. Tozalash uchun matn
        returns: dict

        Usage:
        korrektor = Client(token=<token>)
        response = await korrektor.rem_modifiers(text="Uning ko'zlari ajablantirmoqda-ku")
        """
        if not text:
            return {
                "status": "unsuccessful",
                "code": 4,
                "description": "Foydalanish uchun \n\tkorrektor = Client(token=<token>)\n"
                               "\tresponse = await korrektor.rem_modifiers(text=\"Uning ko'zlari ajablantirmoqda-ku\")"

            }
        data = FormData()
        data.add_field(name="text", value=text)
        response = await self._send_request(endpoint="/remModifiers", data=data)
        return response

    async def tokenize(self, word: str) -> dict:
        """
        :param word: str => Majburiy. Bo’ginlarga ajratish uchun so’z
        :return: dict

        Usage:
        korrektor = Client(token=<token>)
        response = await korrektor.tokenize(word="olamning")        
        """

        if not word:
            return {
                "status": "unsuccessful",
                "code": 4,
                "description": "Foydalanish uchun \n\tkorrektor = Client(token=<token>)\n"
                               "\tresponse = await korrektor.tokenize(word=\"olamning\")"
            }
        data = FormData()
        data.add_field(name="word", value=word)
        response = await self._send_request(endpoint="/tokenize", data=data)
        return response

    async def num2words(self, num: int) -> dict:
        """
        :param num: int => Majburiy. So’zlarda ifodalash uchun son
        :return: dict

        Usage:
        korrektor = Client(token=<token>)
        response = await korrektor.tokenize(word="olamning")
        """
        if not num:
            return {
                "status": "unsuccessful",
                "code": 5,
                "description": "Foydalanish uchun \n\tkorrektor = Client(token=<token>)\n"
                               "\tresponse = await korrektor.num2words(num=24563)"
            }
        data = FormData()
        data.add_field(name='num', value=num)
        response = await self._send_request(endpoint='/numToWords', data=data)
        return response

    async def word_frequency(self, text: str) -> dict:
        """
        :param text: str => Majburiy. So’zlar chastotasini hisoblash uchun matn
        :return: dict

        Usage:
        korrektor = Client(token=<token>)
        response = await korrektor.word_frequency(text="Bugun ajoyib kun. Men bugun ajoyib yangi ishlarni amalga oshiraman.")
        """
        if not text:
            return {
                "status": "unsuccessful",
                "code": 6,
                "description": "Foydalanish uchun \n\tkorrektor = Client(token=<token>)\n"
                               "\tresponse = await korrektor.word_frequency(text=\"Bugun ajoyib kun. Men bugun ajoyib yangi ishlarni amalga oshiraman.\")"
            }
        data = FormData()
        data.add_field(name="text", value=text)
        response = await self._send_request(endpoint="/wordFrequency", data=data)
        return response

    async def remove_duplicates(self, text: str) -> dict:
        """
        :param text: str => Majburiy. Dublikatlarni o’chirish uchun uchun matn
        :return: dict

        Usage:
        korrektor = Client(token=<token>)
        response = await korrektor.remove_duplicates(text="salom salom dunyo")
        """
        if not text:
            return {
                "status": "unsuccessful",
                "code": 7,
                "description": "Foydalanish uchun \n\tkorrektor = Client(token=<token>)\n"
                               "\tresponse = await korrektor.remove_duplicates(text=\"salom salom dunyo\")"
            }
        data = FormData()
        data.add_field(name="text", value=text)
        response = await self._send_request(endpoint="/removeDuplicates", data=data)
        return response

    async def alphabet_sorting(self, text: str) -> dict:
        """
        :param text: str => Majburiy. Saralash uchun uchun matn
        :return: dict:

        Usage:
        korrektor = Client(token=<token>)
        response = await korrektor.alphabet_sorting(text="salom salom dunyo")
        """
        if not text:
            return {
                "status": "unsuccessful",
                "code": 8,
                "description": "Foydalanish uchun \n\tkorrektor = Client(token=<token>)\n"
                               "\tresponse = await korrektor.alphabet_sorting(text=\"salom salom dunyo\")"
            }
        data = FormData()
        data.add_field(name="text", value=text)
        response = await self._send_request(endpoint="/alphabetSorting", data=data)
        return response

    async def ocr(self, image: str) -> dict:
        """
        :param image: str => Majburiy. OCR uchun uchun rasm, file path
        :return: dict:

        Usage:
        korrektor = Client(token=<token>)
        response = await korrektor.ocr(image="image.png")
        """
        if not image:
            return {
                "status": "unsuccessful",
                "code": 9,
                "description": "Foydalanish uchun \n\tkorrektor = Client(token=<token>)\n"
                               "\tresponse = await korrektor.ocr(image=\"image.png\")"
            }
        data = FormData()
        image = open(image, 'rb')
        data.add_field(name="image", value=image)
        response = await self._send_request(endpoint="/ocr", data=data)
        return response

    async def doc(self, doc: str, alphabet: str) -> dict:
        """
        :param doc: str => Majburiy. Qayta ishlash uchun fayl, file path
        :param alphabet: str => Majburiy. Majburiy. Hujjatni qaysi alifboga o’girish. cyrillic yoki latin
        :return: dict:
        """
        if not doc or not alphabet:
            return {
                "status": "unsuccessful",
                "code": 10,
                "description": "Foydalanish uchun \n\tkorrektor = Client(token=<token>)\n"
                               "\tresponse = await korrektor.doc(doc=\"doc.docx\", alphabet=\"cyrillic\")"
            }
        allowed_types = [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/epub+zip",
            "text/html",
        ]
        import mimetypes
        mimetype = mimetypes.guess_type(doc)[0]
        if not mimetype in allowed_types:
            return {
                "status": "unsuccessful",
                "code": 11,
                "description": "Faqatgina *docx, xlsx, pptx, epub va html* formatdagi hujjatlar"
                               " bu metoddan foydalanishi mumkin. Foydalanish uchun \n"
                               "\tkorrektor = Client(token=<token>)\n"
                               "\tresponse = await korrektor.doc(doc=\"doc.docx\", alphabet=\"cyrillic\")"
            }
        data = FormData()
        doc = open(doc, 'rb')
        data.add_field(name="doc", value=doc)
        data.add_field(name="alphabet", value=alphabet)
        response = await self._send_document(endpoint="/doc", data=data)

        return response
