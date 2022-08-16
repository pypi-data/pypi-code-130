from collections import OrderedDict
from typing import Optional

from iterable_serialization import deserialize_iterable
from pronunciation_dictionary import Pronunciation, Pronunciations, Word

Annotation = str


def is_annotation(word: Word, indicator: Optional[str]) -> bool:
  assert isinstance(word, str)
  assert indicator is None or isinstance(indicator, str)
  if len(word) == 0:
    return False

  if indicator is None or len(indicator) == 0:
    return True

  has_at_least_one_annotated_symbol = len(word) > len(indicator) * 2

  if not has_at_least_one_annotated_symbol:
    return False

  first_and_last_is_indicator = word[0] == indicator and word[-1] == indicator

  return first_and_last_is_indicator


def get_pronunciations_from_annotation(annotation: Annotation, indicator: Optional[str], separator: Optional[str], weight: float) -> Pronunciations:
  assert isinstance(weight, float)
  assert weight > 0

  pronunciation = get_annotation_content(annotation, indicator, separator)
  result = OrderedDict((
    (pronunciation, weight),
  ))

  return result


def get_annotation_content(annotation: Annotation, indicator: Optional[str], separator: Optional[str]) -> Pronunciation:
  assert is_annotation(annotation, indicator)
  assert separator is None or (isinstance(separator, str) and len(separator) <= 1)

  indicator_len = 0
  if indicator is not None:
    indicator_len = len(indicator)

  if indicator_len == 0:
    annotation_content = annotation
  else:
    annotation_content = annotation[indicator_len:-indicator_len]
  assert len(annotation_content) > 0

  pronunciation = tuple(deserialize_iterable(annotation_content, separator))
  return pronunciation
