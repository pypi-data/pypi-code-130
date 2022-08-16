from argparse import ArgumentParser, Namespace
from collections import OrderedDict
from functools import partial
from logging import getLogger
from multiprocessing.pool import Pool
from pathlib import Path
from tempfile import gettempdir
from typing import Dict, Optional, Tuple

from ordered_set import OrderedSet
from pronunciation_dictionary import (PronunciationDict, Pronunciations, SerializationOptions, Word,
                                      save_dict)
from tqdm import tqdm

from dict_from_annotation.annotation_handling import (get_pronunciations_from_annotation,
                                                      is_annotation)
from dict_from_annotation.argparse_helper import (add_chunksize_argument, add_encoding_argument,
                                                  add_maxtaskperchild_argument, add_n_jobs_argument,
                                                  add_serialization_group, get_optional,
                                                  parse_existing_file, parse_path,
                                                  parse_positive_float, parse_zero_or_one_char)


def get_parser(parser: ArgumentParser):
  default_rest_out = Path(gettempdir()) / "rest.txt"
  parser.description = "Create pronunciation dictionary for all annotations in a given vocabulary file."
  # todo support multiple files
  parser.add_argument("vocabulary", metavar='vocabulary', type=parse_existing_file,
                      help="file containing the vocabulary (words/annotations separated by line)")
  parser.add_argument("dictionary", metavar='dictionary', type=parse_path,
                      help="path to output created dictionary")
  parser.add_argument("--indicator", type=get_optional(str),
                      help="indicator for an annotation (can also be empty)", default="/")
  parser.add_argument("--separator", type=get_optional(parse_zero_or_one_char),
                      metavar='SYMBOL', help="separator of symbols in an annotation (has to be empty or a single character)", default="|")
  parser.add_argument("--weight", type=parse_positive_float,
                      help="weight to assign for each annotation", default=1.0)
  parser.add_argument("--rest-out", metavar="PATH", type=get_optional(parse_path),
                      help="write non-annotations to this file (same encoding as vocabulary)", default=default_rest_out)
  add_encoding_argument(parser, "--vocabulary-encoding", "encoding of vocabulary")
  add_serialization_group(parser)
  mp_group = parser.add_argument_group("multiprocessing arguments")
  add_n_jobs_argument(mp_group)
  add_chunksize_argument(mp_group)
  add_maxtaskperchild_argument(mp_group)
  return get_pronunciations_files


def get_pronunciations_files(ns: Namespace) -> bool:
  assert ns.vocabulary.is_file()
  logger = getLogger(__name__)

  try:
    vocabulary_content = ns.vocabulary.read_text(ns.vocabulary_encoding)
  except Exception as ex:
    logger.error("Vocabulary couldn't be read.")
    return False

  vocabulary_words = OrderedSet(vocabulary_content.splitlines())

  dictionary_instance, unresolved_words = get_pronunciations(
    vocabulary_words, ns.indicator, ns.separator, ns.weight, ns.n_jobs, ns.maxtasksperchild, ns.chunksize)
  s_options = SerializationOptions(ns.parts_sep, ns.include_numbers, ns.include_weights)

  try:
    save_dict(dictionary_instance, ns.dictionary, ns.serialization_encoding, s_options)
  except Exception as ex:
    logger.error("Dictionary couldn't be written.")
    logger.debug(ex)
    return False

  logger.info(f"Written dictionary to: {ns.dictionary.absolute()}")

  if len(unresolved_words) > 0:
    logger.warning("Not all words were annotations!")
    if ns.rest_out is not None:
      unresolved_out_content = "\n".join(unresolved_words)
      ns.rest_out.parent.mkdir(parents=True, exist_ok=True)
      try:
        ns.rest_out.write_text(unresolved_out_content, "UTF-8")
      except Exception as ex:
        logger.error("Unresolved output couldn't be created!")
        return False
      logger.info(f"Written unresolved to: {ns.rest_out.absolute()}")
  else:
    logger.info("Complete vocabulary is contained in output!")

  return True


def get_pronunciations(vocabulary: OrderedSet[Word], indicator: Optional[str], separator: Optional[str], weight: float, n_jobs: int, maxtasksperchild: Optional[int], chunksize: int) -> Tuple[PronunciationDict, OrderedSet[Word]]:
  lookup_method = partial(
    process_get_pronunciation,
    indicator=indicator,
    separator=separator,
    weight=weight,
  )

  with Pool(
    processes=n_jobs,
    initializer=__init_pool_prepare_cache_mp,
    initargs=(vocabulary,),
    maxtasksperchild=maxtasksperchild,
  ) as pool:
    entries = range(len(vocabulary))
    iterator = pool.imap(lookup_method, entries, chunksize)
    pronunciations_to_i = dict(tqdm(iterator, total=len(entries), unit="words"))

  return get_dictionary(pronunciations_to_i, vocabulary)


def get_dictionary(pronunciations_to_i: Dict[int, Pronunciations], vocabulary: OrderedSet[Word]) -> Tuple[PronunciationDict, OrderedSet[Word]]:
  resulting_dict = OrderedDict()
  unresolved_words = OrderedSet()

  for i, word in enumerate(vocabulary):
    pronunciations = pronunciations_to_i[i]

    if pronunciations is None:
      unresolved_words.add(word)
      continue
    assert word not in resulting_dict
    resulting_dict[word] = pronunciations

  return resulting_dict, unresolved_words


process_unique_words: OrderedSet[Word] = None


def __init_pool_prepare_cache_mp(words: OrderedSet[Word]) -> None:
  global process_unique_words
  process_unique_words = words


def process_get_pronunciation(word_i: int, indicator: Optional[str], separator: Optional[str], weight: float) -> Tuple[int, Optional[Pronunciations]]:
  global process_unique_words
  assert 0 <= word_i < len(process_unique_words)
  word = process_unique_words[word_i]
  pronunciations = None
  if is_annotation(word, indicator):
    annotation = word
    try:
      pronunciations = get_pronunciations_from_annotation(
          annotation, indicator, separator, weight)
    except ValueError as error:
      logger = getLogger(__name__)
      logger.error(f"Annotation '{word}' couldn't be resolved!")
      logger.debug(error)

  return word_i, pronunciations
