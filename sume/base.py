# -*- coding: utf-8 -*-
"""Base structures and functions for the sume module.

Base contains the Sentence, LoadFile and State classes.

author: florian boudin (florian.boudin@univ-nantes.fr)
version: 0.1
date: Nov. 2014
"""

from __future__ import unicode_literals

from collections import Counter

import codecs
import os
import re


class State(object):
    """State class.

    Internal class used as a structure to keep track of the search state in
    the tabu_search method.

    Args:
        subset (set): a subset of sentences
        concepts (Counter): a set of concepts for the subset
        length (int): the length in words
        score (int): the score for the subset

    """

    def __init__(self):
        """Construct a State object."""
        self.subset = set()
        self.concepts = Counter()
        self.length = 0
        self.score = 0


class Sentence(object):
    """The sentence data structure.

    Args:
        tokens (list of str): the list of word tokens.
        doc_id (str): the identifier of the document from which the sentence
          comes from.
        position (int): the position of the sentence in the source document.

    """

    def __init__(self, tokens, doc_id, position):
        """Construct a sentence."""
        self.tokens = tokens
        """ tokens as a list. """

        self.doc_id = doc_id
        """ document identifier of the sentence. """

        self.position = position
        """ position of the sentence within the document. """

        self.concepts = []
        """ concepts of the sentence. """

        self.untokenized_form = ''
        """ untokenized form of the sentence. """

        self.length = 0
        """ length of the untokenized sentence. """


class LoadFile(object):
    """Objects which inherit from this class have read file functions."""

    def __init__(self, input_directory):
        """Construct a file loader.

        Args:
            input_file (str): the path of the input file.
            use_stems (bool): whether stems should be used instead of words,
              defaults to False.

        """
        self.input_directory = input_directory
        self.sentences = []

    def read_documents(self, file_extension=".txt"):
        """Read the input files in the given directory.

        Load the input files and populate the sentence list. Input files are
        expected to be in one tokenized sentence per line format.

        Args:
            file_extension (str): the file extension for input documents,
              defaults to .txt.

        """
        for infile in os.listdir(self.input_directory):

            # skip files with wrong extension
            if not infile.endswith(file_extension):
                continue

            with codecs.open(os.path.join(self.input_directory, infile),
                             'r',
                             'utf-8') as f:

                # loop over sentences
                for i, line in enumerate(f.readlines()):

                    # split the sentence into tokens
                    tokens = line.strip().split(' ')

                    # add the sentence
                    if len(tokens) > 0:
                        sentence = Sentence(tokens, infile, i)
                        untokenized_form = untokenize(tokens)
                        sentence.untokenized_form = untokenized_form
                        sentence.length = len(untokenized_form.split(' '))
                        self.sentences.append(sentence)


def untokenize(tokens):
    """Untokenize a list of tokens.

    Args:
        tokens (list of str): the list of tokens to untokenize.

    Returns:
        a string

    """
    text = ' '.join(tokens)
    text = re.sub(r"\s+", r" ", text.strip())
    text = re.sub(r" ('[a-z]) ", "\g<1> ", text)
    text = re.sub(r" ([\.;,-]) ", "\g<1> ", text)
    text = re.sub(r" ([\.;,-?!])$", "\g<1>", text)
    text = re.sub(r" _ (.+) _ ", " _\g<1>_ ", text)
    text = re.sub(r" \$ ([\d\.]+) ", " $\g<1> ", text)
    text = text.replace(" ' ", "' ")
    text = re.sub(r"([\W\s])\( ", "\g<1>(", text)
    text = re.sub(r" \)([\W\s])", ")\g<1>", text)
    text = text.replace("`` ", "``")
    text = text.replace(" ''", "''")
    text = text.replace(" n't", "n't")
    text = re.sub(r'(^| )" ([^"]+) "( |$)', '\g<1>"\g<2>"\g<3>', text)

    # times
    text = re.sub(r'(\d+) : (\d+ [ap]\.m\.)', '\g<1>:\g<2>', text)

    text = re.sub(r'^" ', '"', text)
    text = re.sub(r' "$', '"', text)
    text = re.sub(r"\s+", " ", text.strip())

    return text
