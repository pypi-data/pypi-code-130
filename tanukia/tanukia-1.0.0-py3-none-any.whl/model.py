from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass(frozen = True)
class BaseTanu:
  data : Dict[str, Any] = field(repr=False)
  """데이터 Dict"""

@dataclass(frozen = True)
class HitoTanu(BaseTanu):
  status : Optional[str] = field(repr=True, compare=True, default=None)
  """시작언어"""
  id : Optional[str] = field(repr=True, compare=True, default=None)
  """도착언어"""
  type : Optional[str] = field(repr=True, compare=True, default=None)
  """번역된 글자"""
  date : Optional[str] = field(repr=True, compare=True, default=None)
  """엔진 유형"""
  title : Optional[str] = field(repr=True, compare=True, default=None)
  """제목"""
  language_localname : Optional[str] = field(repr=True, compare=True, default=None)
  """언어 이름"""
  language : Optional[str] = field(repr=True, compare=True, default=None)
  """언어"""
  languages : List[str] = field(repr=True, compare=True, default=None)
  """다양한 정보"""
  files : List[str] = field(repr=True, compare=True, default=None)
  """파일 List"""
  related : List[str] = field(repr=True, compare=True, default=None)
  """관련정보"""
  tags : List[str] = field(repr=True, compare=True, default=None)
  """태그목록"""
  artists : List[str] = field(repr=True, compare=True, default=None)
  """아티스트"""
  characters : Optional[Any] = field(repr=True, compare=True, default=None)
  """캐릭터"""
  groups : List[str] = field(repr=True, compare=True, default=None)
  """그룹"""
  parodys : List[str] = field(repr=True, compare=True, default=None)
  """"""