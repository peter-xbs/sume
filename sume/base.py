# -*- coding: utf-8 -*-
"""Base structures and functions for the sume module."""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import re
import glob
import codecs

class Sentence:
    """The sentence data structure.

    Args: 
        tokens (list of str): the list of word tokens.
        doc_id (str): the identifier of the document from which the sentence
          comes from.
        position (int): the position of the sentence in the source document.
    """
    def __init__(self, tokens, doc_id, position):

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
        """
        Args:
            input_directory (str): path to the input files.
        """

        self.input_directory = input_directory
        """ path to input files. """

        self.sentences = []
        """ sentences container. """

    def read_documents(self, file_extension="txt"):
        """Read the input files in the given directory.

        Load the input files and populate the sentence list. Input files are
        expected to be in one tokenized sentence per line format.

        Args:
            file_extension (str): the file extension for input documents,
              defaults to txt.
        """

        for input_file in glob.glob(self.input_directory+'/*.'+file_extension):

            with codecs.open(input_file, 'r', 'utf-8') as f:

                # load the sentences
                lines = f.readlines()

                # loop over sentences
                for i in range(len(lines)):

                    # split the sentence into tokens
                    tokens = lines[i].strip().split(' ')

                    # add the sentence
                    if len(tokens) > 0:
                        sentence = Sentence(tokens, input_file, i)
                        untokenized_form = self._untokenize(tokens)
                        sentence.untokenized_form = untokenized_form
                        sentence.length = len(untokenized_form.split(' '))
                        self.sentences.append(sentence)

    def prune_sentences(self,
                        mininum_sentence_length=5,
                        maximum_sentence_length=30,
                        remove_citations=True,
                        remove_redundancy=True):
        """Prune the sentences.

        Remove the sentences that are shorter than a given length, redundant
        sentences and citations from entering the summary.

        Args:
            mininum_sentence_length (int): the minimum number of words for a
                sentence to enter the summary, defaults to 5
            maximum_sentence_length (int): the maximum number of words for a
                sentence to enter the summary, defaults to 30
            remove_citations (bool): indicates that citations are pruned,
                defaults to True
            remove_redundancy (bool): indicates that redundant sentences are
                pruned, defaults to True

        """
        pruned_sentences = []

        # loop over the sentences
        for sentence in self.sentences:

            # prune short sentences
            if sentence.length < mininum_sentence_length:
                continue

            # prune long sentences
            if sentence.length > maximum_sentence_length:
                continue

            # prune citations
            first_token, last_token = sentence.tokens[0], sentence.tokens[-1]
            if remove_citations and \
               (first_token == u"``" or first_token == u'"') and \
               (last_token == u"''" or first_token == u'"'):
                continue

            # prune identical and almost identical sentences
            if remove_redundancy:
                is_redundant = False
                for prev_sentence in pruned_sentences:
                    if sentence.tokens == prev_sentence.tokens:
                        is_redundant = True
                        break

                if is_redundant:
                    continue

            # otherwise add the sentence to the pruned sentence container
            pruned_sentences.append(sentence)

        self.sentences = pruned_sentences

    def _untokenize(self, tokens):
        """Untokenizing a list of tokens. 

        Args:
            tokens (list of str): the list of tokens to untokenize.

        Returns:
            a string

        """
        text = u' '.join(tokens)
        text = re.sub(u"\s+", u" ", text.strip())
        text = re.sub(u" ('[a-z]) ", u"\g<1> ", text)
        text = re.sub(u" ([\.;,-]) ", u"\g<1> ", text)
        text = re.sub(u" ([\.;,-?!])$", u"\g<1>", text)
        text = re.sub(u" _ (.+) _ ", u" _\g<1>_ ", text)
        text = re.sub(u" \$ ([\d\.]+) ", u" $\g<1> ", text)
        text = text.replace(u" ' ", u"' ")
        text = re.sub(u"([\W\s])\( ", u"\g<1>(", text)
        text = re.sub(u" \)([\W\s])", u")\g<1>", text)
        text = text.replace(u"`` ", u"``")
        text = text.replace(u" ''", u"''")
        text = text.replace(u" n't", u"n't")
        text = re.sub(u'(^| )" ([^"]+) "( |$)', u'\g<1>"\g<2>"\g<3>', text)

        # times
        text = re.sub('(\d+) : (\d+ [ap]\.m\.)', '\g<1>:\g<2>', text)

        text = re.sub('^" ', '"', text)
        text = re.sub(' "$', '"', text)
        text = re.sub(u"\s+", u" ", text.strip())

        return text

