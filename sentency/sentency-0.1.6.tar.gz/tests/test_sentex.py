#!/usr/bin/env python

"""Tests for `sentency` package."""
import spacy

from sentency.regex import regexize_keywords
from sentency.sentency import Sentex

from .config import aaa_keywords, ignore_keywords


def test_sentex():
    text = """
    Screening for abdominal aortic aneurysm.
    Impression: There is evidence of a fusiform
    abdominal aortic aneurysm measuring 3.4 cm.
    """
    keyword_regex = regexize_keywords(aaa_keywords)
    ignore_regex = regexize_keywords(ignore_keywords)

    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe(
        "sentex", config={"sentence_regex": keyword_regex, "ignore_regex": ignore_regex}
    )

    doc = nlp(text)

    assert len(doc._.sentex) == 1


def test_sentex_annotate_ents():
    text = """
    Screening for abdominal aortic aneurysm.
    Impression: There is evidence of a fusiform
    abdominal aortic aneurysm measuring 3.4 cm.
    """
    keyword_regex = regexize_keywords(aaa_keywords)
    ignore_regex = regexize_keywords(ignore_keywords)

    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe(
        "sentex",
        config={
            "sentence_regex": keyword_regex,
            "ignore_regex": ignore_regex,
            "annotate_ents": True,
            "label": "AAA",
        },
    )

    doc = nlp(text)

    assert doc.ents[0].text == "abdominal aortic aneurysm"


def test_sentex_annotate_ents_expand_mode():
    text = "Patient was aggressive. Other patient was aggressive."
    keyword_regex = "(?i)aggress"

    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe(
        "sentex",
        config={
            "sentence_regex": keyword_regex,
            "annotate_ents": True,
            "label": "NEG_DESC",
        },
    )

    doc = nlp(text)

    assert doc.ents[0].text == "aggressive"
    assert doc.ents[1].text == "aggressive"
