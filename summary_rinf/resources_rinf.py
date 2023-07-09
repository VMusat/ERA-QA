import pprint
import elastic_conn as ec
import aux_functions as af


class Resources:

    def __init__(self):
        self.aux = af.AuxFunc()

    def get_property_values(self, entity, property):
        result = []
        prop_result = self.aux.query_rinf_prop(entity)
        for key, value in prop_result.items():
            if key == property:
                for elem in value['values']:
                    for k, v in elem.items():
                        result.append({'id': k, 'value': v})
        return result

    def get_properties(self, entity):
        result = []
        prop_result = self.aux.query_rinf_prop(entity)
        for key, value in prop_result.items():
            result.append({'id': key, 'value': value['label']})
        return result

    def find_resources(self, label, max_candidates=4, ignore_net=True):
        conn = ec.Connection()
        candidates = []
        elastic_result = conn.generate_query(label)
        candidate_uris = {}
        for doc_elem in elastic_result['hits']['hits']:
            aux_list = doc_elem['_source']['uris'][0]
            for uri in aux_list:
                netEl = 'http://data.europa.eu/949/topology/netElements/'
                if netEl in uri:
                    aux_list.remove(uri)
            candidate_uris[doc_elem['_source']['label']] = aux_list

        count = 0
        for label, uris in candidate_uris.items():
            for uri in uris:
                if count < max_candidates:
                    candidate = {
                        'label': label,
                        'id': uri,
                        'description': "",
                        'properties': self.get_properties(uri)
                    }
                    # pprint.pprint(candidate)
                    candidates.append(candidate)
                    count = count + 1
                else:
                    break
        return candidates
