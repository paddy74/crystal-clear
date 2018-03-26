"""Tests for language_translation module

"""
from .. import language_translation as lt


def run_tests():
    """Run all the tests for the module
    """
    test_translator()


def test_translator():
    """Tests the Translator class
    """
    t = lt.Translator("english", "spanish")
    word = "chair"

    t_word = "silla"

    if t.translate(word)[0] is not t_word:
        print("Bleh")
