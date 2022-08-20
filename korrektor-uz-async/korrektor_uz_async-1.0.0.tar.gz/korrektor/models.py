import json
import typing

from pydantic import BaseModel


class Response(BaseModel):
    status: str
    code: int

    def __dict__(self):
        return {
            'status': self.status,
            'code': self.code
        }


class Text(BaseModel):
    text: str

    def __dict__(self):
        return {
            "text": self.text
        }


class SpellCheckResult(BaseModel):
    word: str
    status: str
    suggestion: typing.List[str] = None

    def __dict__(self):
        return {
            "word": self.word,
            "status": self.status,
            "suggestion": self.suggestion
        }


class SpellCheckRequest(BaseModel):
    remove_modifiers: bool = False
    words: typing.List[str]

    def __dict__(self):
        return {
            "remove_modifiers": self.remove_modifiers,
            "words": self.words
        }

    def __json__(self):
        return json.dumps(dict(self))


class SpellCheckResponse(Response, BaseModel):
    data: typing.List[SpellCheckResult]

    def __dict__(self):
        return {
            "status": self.status,
            "code": self.code,
            "data": self.data
        }


class TransliterationRequest(BaseModel):
    alphabet: str
    text: str

    def __dict__(self):
        return {
            "alphabet": self.alphabet,
            "text": self.text
        }

    def __json__(self):
        return json.dumps(dict(self))


class TransliterationResponse(Response, BaseModel):
    text: str

    def __dict__(self):
        return {
            "status": self.status,
            "code": self.code,
            "text": self.text
        }


class AutoCorrextRequest(BaseModel):
    text: str

    def __dict__(self):
        return {
            "text": self.text
        }

    def __json__(self):
        return json.dumps(dict(self))


class AutoCorrextResponse(Response, BaseModel):
    text: str

    def __dict__(self):
        return {
            "status": self.status,
            "code": self.code,
            "text": self.text
        }


class RemModifiersRequest(BaseModel):
    text: str

    def __dict__(self):
        return {
            "text": self.text
        }

    def __json__(self):
        return json.dumps(dict(self))


class RemModifiersResponse(Response, BaseModel):
    text: str

    def __dict__(self):
        return {
            "status": self.status,
            "code": self.code,
            "text": self.text
        }


class TokenizationRequest(BaseModel):
    word: str

    def __dict__(self):
        return {
            "word": self.word
        }

    def __json__(self):
        return json.dumps(dict(self))


class TokenizationResponse(Response, BaseModel):
    text: str

    def __dict__(self):
        return {
            "status": self.status,
            "code": self.code,
            "text": self.text
        }


class NumToWordsRequest(BaseModel):
    num: int

    def __dict__(self):
        return {
            "num": self.num
        }

    def __json__(self):
        return json.dumps(dict(self))


class NumToWordsResponse(Response, BaseModel):
    text: str

    def __dict__(self):
        return {
            "status": self.status,
            "code": self.code,
            "text": self.text
        }


class WordFrequencyRequest(BaseModel):
    text: str

    def __dict__(self):
        return {
            "text": self.text
        }

    def __json__(self):
        return json.dumps(dict(self))


class WordFrequencyResponse(Response, BaseModel):
    data: typing.Dict[str, int] = {}

    def __dict__(self):
        return {
            "status": self.status,
            "code": self.code,
            "data": self.data
        }


class RemoveDuplicatesRequest(BaseModel):
    text: str

    def __dict__(self):
        return {
            "text": self.text
        }

    def __json__(self):
        return json.dumps(dict(self))


class RemoveDuplicatesResponse(Response, BaseModel):
    text: str

    def __dict__(self):
        return {
            "status": self.status,
            "code": self.code,
            "text": self.text
        }


class AlphabetSortingRequest(BaseModel):
    text: str

    def __dict__(self):
        return {
            "text": self.text
        }

    def __json__(self):
        return json.dumps(dict(self))


class AlphabetSortingResponse(Response, BaseModel):
    text: str

    def __dict__(self):
        return {
            "status": self.status,
            "code": self.code,
            "text": self.text
        }


class OCRRequest(BaseModel):
    image: bytes

    def __dict__(self):
        return {
            "image": self.image
        }


class OCRResponse(Response, BaseModel):
    text: str

    def __dict__(self):
        return {
            "status": self.status,
            "code": self.code,
            "text": self.text
        }


class TransliterateFileRequest(BaseModel):
    doc: bytes
    alphabet: str

    def __dict__(self):
        return {
            "doc": self.doc,
            "alphabet": self.alphabet
        }
