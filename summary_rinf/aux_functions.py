import pprint
import re
import random
import pyoxigraph as po
from pyoxigraph import Store
import json


class AuxFunc:

    def __init__(self):
        self.store = Store(path="C:/Users/valii/PycharmProjects/KGQA/ERA-QA/graph")

    def query_rinf_prop(self, entity):
        store = self.store
        # Obtaining the rinf graph
        ans = store.named_graphs().__next__()
        # print(ans)
        prop_list = {}
        entity = "<" + entity + ">"
        backw = """                 UNION
                                    {{ ?s ?prop {0} }}"""
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

            if solution['b_lab'] is not None:
                label = str(solution['b_lab'].value)
            else:
                try:
                    label = str(solution['b'].value).split("/")[-3]
                except IndexError:
                    label = str(solution['b'].value).split("/")[-1]

            prop_list[solution['prop'].value].setdefault('values', []).append({solution['b'].value: label})

        if prop_list.__contains__('http://www.w3.org/2000/01/rdf-schema#label'):
            prop_list.pop("http://www.w3.org/2000/01/rdf-schema#label")

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
        # print(solution['subject'].value)
        sol_dict.setdefault(solution['label'].value, []).append(solution['subject'].value)

    # pprint.pprint(sol_dict)
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
        # print(solution['subject'].value)
        sol_dict.setdefault(str(solution['label'].value).split("/")[-1], []).append(solution['subject'].value)

    # pprint.pprint(sol_dict)
    json_data = json.dumps(sol_dict, ensure_ascii=False, indent=4)
    with open('../abstractions.json', 'w', encoding='utf8') as file:
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
# op = "http://data.europa.eu/949/functionalInfrastructure/tracks/ES70004_110020%2001"
# sol_dict = AuxFunc().query_rinf_prop(op)
# pprint.pprint(sol_dict)
# generate_prop_from_labels()
# pprint.pprint(query_rinf_prop_values(prop_list, op))
