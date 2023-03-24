import logging

# PoS tagger
import re
from flair.data import Sentence, Token, Tokenizer
from flair.models import SequenceTagger
from flair.tokenization import SegtokTokenizer
from typing import List

class Concept:

    def __init__(self):
        logging.getLogger("flair").setLevel(level=logging.WARNING)
        self.logger = logging.getLogger('muheqa')
        self.logger.debug("initializing Concept class instance...")

        pos_language_model = "flair/pos-english"
        self.ner_tagger = SequenceTagger.load(pos_language_model)

    def get(self, text):
        self.logger.debug("getting concepts ...")
        main_categories = ['CD', 'NN', 'NNS', 'NNP', 'NNPS']
        additional_categories = ['JJ', 'NNS']
        drop_categories = ['IN', 'WRB', 'CC']

        # make sentence
        sentence = Sentence(text)
        print(sentence)
        # iterate over the tokens and modify their text if they contain an underscore
        new_tokens = []
        previous = ""
        next_flag = False
        semitoken = ""
        for token in sentence:
            # print("." + token.text + ".")
            if next_flag:
                new_token = Token(semitoken + token.text)
                new_tokens.append(new_token)
                previous = new_token.text
                # previous, semitoken = "", ""
                next_flag = False
            else:
                if "_" in token.text:
                    # create a new token with the desired text
                    next_flag = True
                    new_tokens.pop()
                    semitoken = previous + "_"
                else:
                    previous = token.text
                    new_tokens.append(token)
        # replace the old tokens with the new ones in the sentence
        sentence.tokens = new_tokens


        self.ner_tagger.predict(sentence)

        # iterate over tokens
        concepts = []
        current_concept = ""
        partial_concept = ""
        previous_token = ""
        for t in sentence.tokens:
            for label in t.annotation_layers.keys():
                token = t.text
                category = t.get_labels(label)[0].value
                self.logger.debug("Token:" + token + " [ " + category + "]  Previous: [" + previous_token + "]")
                # self.logger.debug("Current Concept: " + current_concept + ", Partial Concept: " + partial_concept)
                if (category in main_categories):
                    if (len(partial_concept) > 0):
                        current_concept = partial_concept + " " + token
                        partial_concept = ""
                    elif (current_concept == ""):
                        current_concept += token
                    else:
                        current_concept += " " + token
                elif (category in additional_categories):
                    if (len(current_concept) > 0):
                        current_concept += " " + token
                    elif (len(partial_concept) > 0):
                        partial_concept += " " + token
                    elif (previous_token not in ['WRB', 'CC']):
                        partial_concept += token
                    else:
                        if (len(current_concept) > 0):
                            concepts.append(current_concept)
                        current_concept = ""
                        partial_concept = ""
                elif (category in drop_categories):
                    if (len(current_concept) > 0):
                        concepts.append(current_concept)
                    current_concept = ""
                    partial_concept = ""
                elif len(current_concept) > 0:
                    if (len(current_concept) > 0):
                        concepts.append(current_concept)
                    current_concept = ""
                    partial_concept = ""
            previous_token = t.get_labels(label)[0].value
        if (len(current_concept) > 0):
            concepts.append(current_concept)
        return concepts

