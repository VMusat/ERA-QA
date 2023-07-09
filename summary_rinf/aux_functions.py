import pprint
import re
import random
import pyoxigraph as po
from pyoxigraph import Store
import json
from urllib.parse import unquote
# backw = """                 UNION
#                             {{ ?s ?prop {0} }}"""


class AuxFunc:

    def __init__(self):
        self.store = Store(path="C:/Users/valii/PycharmProjects/KGQA/ERA-QA/graph")

    def query_rinf_prop(self, entity):
        store = self.store
        # Obtaining the rinf graph
        ans = store.named_graphs().__next__()
        prop_list = {}
        entity = "<" + entity + ">"
        quote = """
                                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                                    SELECT distinct ?prop ?b ?p_lab ?b_lab
                                    WHERE
                                    {{
                                        {{ {0} ?prop ?b .}} 
                                        OPTIONAL
                                        {{ ?prop rdfs:label ?p_lab }}
                                        OPTIONAL
                                        {{ ?b rdfs:label ?b_lab }}
                                    }}
                                    """
        quote = quote.format(entity)
        # solution_list = []
        for solution in store.query(quote, default_graph=ans):
            # solution_list.append(solution)
            if solution['p_lab'] is not None:
                label = solution['p_lab'].value
            else:
                label = str(solution['prop'].value).split("/")[-1]

            prop_list.setdefault(solution['prop'].value, {})
            prop_list[solution['prop'].value].setdefault('label', label)

            # Code to obtain the rdf label of the value, removed to obtain complete tracks
            # if solution['b_lab'] is not None:
            #     label = str(solution['b_lab'].value)
            # else:
            # Code to obtain the last 3 elements between slashes of the value
            # try:
            #     label = str(solution['b'].value).split("/")[-3:]
            #     label = "/".join(map(str, label))
            # except IndexError:
            # This would go in the else.
            label = str(solution['b'].value).split("/")[-1]

            prop_list[solution['prop'].value].setdefault('values', []).append({solution['b'].value: label})

        if prop_list.__contains__('http://www.w3.org/2000/01/rdf-schema#label'):
            prop_list.pop("http://www.w3.org/2000/01/rdf-schema#label")

        # pprint.pprint(prop_list)
        return prop_list


def query_rinf_labels():
    store = Store(path="../graph")
    # Obtaining the rinf graph
    ans = store.named_graphs().__next__()
    print(ans)
    sol_dict = {}
    for solution in store.query('''
                                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                                SELECT ?subject ?label
                                WHERE {
                                  ?subject rdfs:label ?label .
                                }''',
                                default_graph=ans):
        sol_dict.setdefault(solution['label'].value, []).append(solution['subject'].value)
    json_data = json.dumps(sol_dict, ensure_ascii=False, indent=4)
    with open('../labels.json', 'w', encoding='utf8') as file:
        file.write(json_data)


def query_rinf_abstractions():
    store = Store(path="../graph")
    # Obtaining the rinf graph
    ans = store.named_graphs().__next__()
    print(ans)
    sol_dict = {}
    for solution in store.query('''
                                SELECT ?subject ?label
                                WHERE {
                                  ?subject <http://data.europa.eu/949/hasAbstraction> ?label .
                                }''',
                                default_graph=ans):
        sol_dict.setdefault(str(solution['label'].value).split("/")[-1], []).append(solution['subject'].value)
    json_data = json.dumps(sol_dict, ensure_ascii=False, indent=4)
    with open('../abstractions.json', 'w', encoding='utf8') as file:
        file.write(json_data)


def query_rinf_uopid():
    store = Store(path="../graph")
    # Obtaining the rinf graph
    ans = store.named_graphs().__next__()
    sol_dict = {}
    for solution in store.query('''
                                SELECT ?subject ?uopid ?track ?label
                                WHERE {
                                  ?subject <http://data.europa.eu/949/uopid> ?uopid .
                                  ?subject <http://data.europa.eu/949/track> ?track .
                                  ?track <http://www.w3.org/2000/01/rdf-schema#label> ?label
                                }''',
                                default_graph=ans):
        uopid_label = str(solution['uopid'].value) + "_" + str(solution['label'].value).split("/")[-1]
        sol_dict.setdefault(uopid_label, []).append(solution['track'].value)
    json_data = json.dumps(sol_dict, ensure_ascii=False, indent=4)
    with open('../uopid.json', 'w', encoding='utf8') as file:
        file.write(json_data)


def query_rinf_specials():
    store = Store(path="../graph")
    ans = store.named_graphs().__next__()
    sol_dict = {}
    for solution in store.query('''
                                SELECT ?subject ?tds ?etcs ?cls
                                WHERE {
                                {?subject <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://data.europa.eu/949/Track> .}
                                  OPTIONAL
                                  {?subject <http://data.europa.eu/949/trainDetectionSystem> ?tds .}
                                  OPTIONAL
                                  {?subject <http://data.europa.eu/949/etcsLevel> ?etcs .}
                                  OPTIONAL
                                  {?subject <http://data.europa.eu/949/contactLineSystem> ?cls .}
                                }''',
                                default_graph=ans):
        tds_label = solution['tds']
        etcs_label = solution['etcs']
        cls_label = solution['cls']
        if tds_label is not None:
            sol_dict.setdefault(str(solution['tds'].value).split("/")[-1], []).append(solution['tds'].value)
        if etcs_label is not None:
            sol_dict.setdefault(str(solution['etcs'].value).split("/")[-1], []).append(solution['etcs'].value)
        if cls_label is not None:
            sol_dict.setdefault(str(solution['cls'].value).split("/")[-1], []).append(solution['cls'].value)
    json_data = json.dumps(sol_dict, ensure_ascii=False, indent=4)
    with open('../specials.json', 'w', encoding='utf8') as file:
        file.write(json_data)


def query_rinf_lineref():
    store = Store(path="../graph")
    # Obtaining the rinf graph
    ans = store.named_graphs().__next__()
    print(ans)
    sol_dict = {}
    for solution in store.query('''
                                SELECT ?subject ?lineref
                                WHERE {
                                  ?subject <http://data.europa.eu/949/lineReference> ?lineref .
                                }''',
                                default_graph=ans):
        line_ref = str(solution['lineref'].value).split("/")[-1]
        sol_dict.setdefault(line_ref, []).append(solution['lineref'].value)
    json_data = json.dumps(sol_dict, ensure_ascii=False, indent=4)
    with open('../line_references.json', 'w', encoding='utf8') as file:
        file.write(json_data)


def merge_abstractions_specials():
    with open('../abstractions.json', 'r', encoding='utf8') as file:
        abstractions_dict = json.load(file)
    with open('../specials.json', 'r', encoding='utf8') as file:
        specials_dict = json.load(file)
    merged_data = {}

    for key in set(list(abstractions_dict.keys()) + list(specials_dict.keys())):
        merged_data[key] = []
        if key in abstractions_dict:
            for value in abstractions_dict[key]:
                merged_data[key].append(value)
        if key in specials_dict:
            for value in specials_dict[key]:
                merged_data[key].append(value)

    json_data = json.dumps(merged_data, ensure_ascii=False, indent=4)
    with open('../merged.json', 'w', encoding='utf8') as file:
        file.write(json_data)


def merge_without_ascii():
    with open('../abstractions.json', 'r', encoding='utf8') as file:
        abstractions_dict = json.load(file)
    with open('../specials.json', 'r', encoding='utf8') as file:
        specials_dict = json.load(file)
    merged_data = {}

    for key in set(list(abstractions_dict.keys()) + list(specials_dict.keys())):
        new_key = unquote(key)
        merged_data[new_key] = []
        if key in abstractions_dict:
            for value in abstractions_dict[key]:
                new_key = unquote(key)
                merged_data[new_key].append(value)
        if key in specials_dict:
            for value in specials_dict[key]:
                new_key = unquote(key)
                merged_data[new_key].append(value)

    json_data = json.dumps(merged_data, ensure_ascii=False, indent=4)
    with open('../no_ascii_merged.json', 'w', encoding='utf8') as file:
        file.write(json_data)


# NOT USED
def generate_prop_from_labels():
    with open('../labels.json', 'r', encoding='utf8') as file_read:
        js = json.load(file_read)
        sol_dict = {}
        for key, value in js.items():
            for entity in value:
                prop_list = query_rinf_prop(entity)
                sol_dict[entity] = prop_list

        print("listo")
        json_data = json.dumps(sol_dict, ensure_ascii=False, indent=4)
        with open('prop.json', 'w', encoding='utf8') as file_write:
            file_write.write(json_data)


# NOT USED, Forward values
def query_rinf_prop_values(prop_list, entity):
    store = Store(path="../graph")
    # Obtaining the rinf graph
    ans = store.named_graphs().__next__()
    entity = "<" + entity + ">"
    sol_list = []
    for prop in prop_list:
        prop = "<" + prop + ">"
        opt = """                       OPTIONAL
                                        {{ ?object rdfs:label ?label }}"""
        quote = """     
                                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                                        SELECT distinct ?obj {{
                                        WHERE
                                        {{
                                        {{ {0} {1} ?obj }}
                                        }} LIMIT 1
                                        """
        quote = quote.format(entity, prop)
        print(quote)
        for solution in store.query(quote, default_graph=ans):
            sol_list.append({"id": solution['object'].value, "label": solution["label"].value})
        return sol_list


# query_rinf_labels()
# query_rinf_abstractions()
# query_rinf_uopid()
# query_rinf_specials()
# query_rinf_lineref()
# merge_abstractions_specials()
# merge_without_ascii()
# op = "http://data.europa.eu/949/functionalInfrastructure/tracks/ES70004_110020%2001"
# sol_dict = AuxFunc().query_rinf_prop(op)
# pprint.pprint(sol_dict)
# generate_prop_from_labels()
# pprint.pprint(query_rinf_prop_values(prop_list, op))
