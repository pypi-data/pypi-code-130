#!/usr/bin/env python

"""Tests for `sentency` package."""

from sentency.regex import regexize_keywords


def test_regexize_keywords():
    keywords = "abdominal aortic aneurysm\naneurysm abdominal aorta"
    actual = regexize_keywords(keywords)
    expected = "(?i)((abdominal.*aortic.*aneurysm)|(aneurysm.*abdominal.*aorta))"
    assert actual == expected


def test_regexize_single():
    keywords = "abdominal"
    actual = regexize_keywords(keywords)
    expected = "(?i)((abdominal))"
    assert actual == expected


def test_regexize_case_sensitive():
    keywords = "abdominal aortic aneurysm\naneurysm abdominal aorta"
    actual = regexize_keywords(keywords, case_insensitive=False)
    expected = "((abdominal.*aortic.*aneurysm)|(aneurysm.*abdominal.*aorta))"
    assert actual == expected


def test_regexize_only_lines():
    keywords = "abdominal\naneurysm"
    actual = regexize_keywords(keywords, case_insensitive=False)
    expected = "((abdominal)|(aneurysm))"
    assert actual == expected


def test_regexize_single_group():
    keywords = "abdominal aortic aneurysm"
    actual = regexize_keywords(keywords, case_insensitive=False)
    expected = "((abdominal.*aortic.*aneurysm))"
    assert actual == expected
