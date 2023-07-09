import pprint

import discovery_rinf as dc
import resources_rinf as rrf
import summarizer_rinf as sr
import MuHeQA.application.evidence.discoverer as ds
import MuHeQA.application.answer.composer as cp


class Tester:

    def get_resources(self, query):
        discovery = dc.Discovery()
        resource = rrf.Resources()

        keys = discovery.get_keywords(query)
        resources_list = []
        print(keys)
        for ent in keys['concepts']:
            candidates = resource.find_resources(ent)
            for cand in candidates:
                resources_list.append(cand['id'])
                print(cand['id'])
            pprint.pprint(resource.find_resources(ent))
        return resources_list

    def get_answer(self, query):
        discoverer = ds.Discoverer()
        composer = cp.Composer()
        summarizer = sr.Summarizer()

        sentences = summarizer.get_sentences(query)
        # pprint.pprint(sentences)

        evidences = discoverer.get_evidences(query, sentences, max=5)

        answers = composer.get_answers(query, evidences, max=5)

        # pprint.pprint(answers)
        return answers


t = Tester()
q = "What is the lineReference of the OperationalPoint Bif de La Pallice (La Rochelle)?"

# Comment one line or the other
# pprint.pprint(t.get_resources(q))
pprint.pprint(t.get_answer(q))


