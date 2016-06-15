#!/usr/bin/env python

import argparse
import functools
import multiprocessing
import sys
import unicodedata
import neologdn



class DocumentNormalizer:
  def __init__(self, language):
    self._language = language

  def normalize(self, document):
    return {
      "english" : normalize_in_english,
      "japanese" : normalize_in_japanese,
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
  arg_parser.add_argument("-l", "--language", default="english")
  return arg_parser.parse_args()


def main():
  args = get_args()

  for document in normalize_documents(args.document_file.readlines(),
                                      args.language):
    print(document)


if __name__ == "__main__":
  main()
