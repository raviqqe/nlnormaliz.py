#!/usr/bin/env python

import argparse
import iso639
import functools
import langdetect
import multiprocessing
import sys
import unicodedata
import neologdn



class DocumentNormalizer:
  def __init__(self, language):
    self._language = language

  def normalize(self, document):
    return {
      "en" : normalize_in_english,
      "ja" : normalize_in_japanese,
    }[self._language](document)


def common_normalization(func):
  @functools.wraps(func)
  def wrapper(document):
    return func(unicodedata.normalize("NFKC", document.strip()))
  return wrapper


@common_normalization
def normalize_in_english(document):
  return document


@common_normalization
def normalize_in_japanese(document):
  return neologdn.normalize(document)


def normalize_documents(documents, language):
  return multiprocessing.Pool().map(DocumentNormalizer(language).normalize,
                                    documents)


def get_args():
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("document_file",
                          nargs="?",
                          type=argparse.FileType(),
                          default=sys.stdin)
  arg_parser.add_argument("-l", "--language", help="ISO 639-1 code.")
  arg_parser.add_argument("-v", "--verbose", action="store_true")
  args = arg_parser.parse_args()

  if args.language is not None and not iso639.is_valid639_1(args.language):
    raise ValueError("\"{}\" is not a valid ISO 639-1 code."
                     .format(args.language))

  return args


def main():
  args = get_args()

  documents = args.document_file.readlines()
  language = langdetect.detect(" ".join(documents)) \
             if args.language is None else args.language

  if args.verbose:
    print("ISO 639-1 code:", language, file=sys.stderr)

  for document in normalize_documents(documents, language):
    print(document)


if __name__ == "__main__":
  main()
