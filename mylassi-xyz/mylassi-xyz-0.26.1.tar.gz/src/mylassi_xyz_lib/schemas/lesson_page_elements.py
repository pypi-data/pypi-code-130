__all__ = [
    'LessonPageElementTypeValues',
    'LessonPageElementStyleData', 'LessonPageElementStyleSchema',
    'LessonPageElementData', 'LessonPageElementSchema',
    'CreateLessonPageElementOptionData', 'CreateLessonPageElementOptionSchema',
    'PatchLessonPageElementOptionData', 'PatchLessonPageElementOptionSchema',
]

import enum
from dataclasses import dataclass, field
from typing import Optional

import marshmallow_dataclass


class LessonPageElementTypeValues(enum.Enum):
    TextElement = 'TextElement'
    MarkdownElement = 'MarkdownElement'
    ImageElement = 'ImageElement'
    YoutubeElement = 'YoutubeElement'


@dataclass
class LessonPageElementStyleData:
    width: Optional[float] = field()
    height: Optional[float] = field()
    top: Optional[float] = field()
    left: Optional[float] = field()

    font_size: Optional[str] = field()
    text_align: Optional[str] = field()


@dataclass
class LessonPageElementData:
    id: int = field()

    type: LessonPageElementTypeValues = field()
    content: str = field()
    style: LessonPageElementStyleData = field()


@dataclass
class CreateLessonPageElementOptionData:
    type: LessonPageElementTypeValues = field()
    content: Optional[str] = field()
    style: Optional[LessonPageElementStyleData] = field()


@dataclass
class PatchLessonPageElementOptionData:
    content: Optional[str] = field()
    style: Optional[LessonPageElementStyleData] = field()


LessonPageElementStyleSchema = marshmallow_dataclass.class_schema(LessonPageElementStyleData)()
LessonPageElementSchema = marshmallow_dataclass.class_schema(LessonPageElementData)()
CreateLessonPageElementOptionSchema = marshmallow_dataclass.class_schema(CreateLessonPageElementOptionData)()
PatchLessonPageElementOptionSchema = marshmallow_dataclass.class_schema(PatchLessonPageElementOptionData)()
