import pprint

import discovery_rinf as dc
import resources_rinf as rrf
import summarizer_rinf as sr
import MuHeQA.application.evidence.discoverer as ds
import MuHeQA.application.answer.composer as cp


def get_resources():
    discovery = dc.Discovery()
    resource = rrf.Resources()

    keys = discovery.get_keywords(query)
    print(keys)
    for ent in keys['concepts']:
        pprint.pprint(resource.find_resources(ent))


def get_answer():
    discoverer = ds.Discoverer()
    composer = cp.Composer()
    summarizer = sr.Summarizer()

    sentences = summarizer.get_sentences(query)
    print(sentences)

    evidences = discoverer.get_evidences(query, sentences, max=5)

    answers = composer.get_answers(query, evidences, max=5)

    pprint.pprint(answers)


query = "What is the Network Coverage of the track 1670_BEMHLG_1395-1_BEMH?"

# get_resources()
get_answer()



