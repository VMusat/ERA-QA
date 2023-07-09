from datetime import datetime
import time
from pyoxigraph import Store
import json
import pprint
from test_rinf import Tester
from urllib.parse import unquote
import pandas as pd


def obtain_triples(entity_type):
    store = Store(path="../graph")
    # Obtaining the rinf graph
    ans = store.named_graphs().__next__()
    print(ans)
    sol_dict = {}
    subjects_list = []
    # Select the number of entities
    prepared_query = '''
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX deu: <http://data.europa.eu/949/>    
                        SELECT ?subject
                        WHERE {{
                            ?subject rdf:type deu:{0} .
                            ?subject ?predicate ?object .
                        }}
                        ORDER BY RAND()
                        LIMIT 15'''
    quote = prepared_query.format(entity_type)
    for solution in store.query(quote, default_graph=ans):
        subjects_list.append(solution['subject'].value)

    for subj in subjects_list:
        entity = "<" + subj + ">"
        # Select the number of properties per entity
        prepared_query = '''
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX deu: <http://data.europa.eu/949/>
                        SELECT ?predicate ?object
                        WHERE {{
                            {0} ?predicate ?object .
                            FILTER(?predicate != rdf:type)
                            FILTER(?predicate != rdfs:label)
                            FILTER(?predicate != deu:notApplicable)
                            FILTER(?predicate != deu:notYetAvailable)
                            FILTER(?predicate != deu:hasAbstraction)
                        }}
                        ORDER BY RAND()
                        LIMIT 12
                        '''
        quote = prepared_query.format(entity)
        for solution in store.query(quote, default_graph=ans):
            sol_dict.setdefault(subj, []).append([solution['predicate'].value, solution['object'].value])
    pprint.pprint(sol_dict)
    return sol_dict


def obtain_labeled_entities(entity_type):
    store = Store(path="../graph")
    # Obtaining the rinf graph
    ans = store.named_graphs().__next__()
    print(ans)
    sol_dict = {}
    subjects_list = []
    labels_list = []
    # Select the number of entities
    prepared_query = '''
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX deu: <http://data.europa.eu/949/>    
                            SELECT ?subject ?label
                            WHERE {{
                                ?subject rdf:type deu:{0} .
                                ?subject ?predicate ?object .
                                ?subject rdfs:label ?label .
                            }}
                            ORDER BY RAND()
                            LIMIT 15'''
    quote = prepared_query.format(entity_type)
    for solution in store.query(quote, default_graph=ans):
        subjects_list.append(solution['subject'].value)
        labels_list.append(solution['label'].value)

    for subj, label in zip(subjects_list, labels_list):
        entity = "<" + subj + ">"
        # Select the number of properties per entity
        prepared_query = '''
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX deu: <http://data.europa.eu/949/>
                            SELECT ?predicate ?object
                            WHERE {{
                                {0} ?predicate ?object .
                                FILTER(?predicate != rdf:type)
                                FILTER(?predicate != rdfs:label)
                                FILTER(?predicate != deu:notApplicable)
                                FILTER(?predicate != deu:notYetAvailable)
                                FILTER(?predicate != deu:hasAbstraction)
                            }}
                            ORDER BY RAND()
                            LIMIT 12
                            '''
        quote = prepared_query.format(entity)
        for solution in store.query(quote, default_graph=ans):
            sol_dict.setdefault(label, []).append([solution['predicate'].value, solution['object'].value])
    pprint.pprint(sol_dict)
    return sol_dict


def generate_questions(df, type, labeled=False):
    if labeled:
        entity_dict = obtain_labeled_entities(type)
    else:
        entity_dict = obtain_triples(type)
    question_list, solution_list, uuid_list, prop_list, type_list = [], [], [], [], []
    for key, value in entity_dict.items():
        name_encoded = str(key).split("/")[-1]
        name = unquote(name_encoded)
        for values in value:
            prop_name = str(values[0]).split("/")[-1]
            prop_value = str(values[1])
            this_id = time.perf_counter()
            if prop_value == 'false' or prop_value == 'true':
                # question = "Do the "+type+" "+name+" has "+prop_name+"?"
                question = "What is the " + prop_name + " of the " + type + " " + name + "?"
                df.loc[this_id, 'question_type'] = 'Boolean'
            else:
                question = "What is the "+prop_name+" of the "+type+" "+name+"?"
                df.loc[this_id, 'question_type'] = 'What'

            question_list.append(question)
            uuid_list.append(this_id)
            solution_list.append(prop_value)
            prop_list.append(prop_name)
            df.loc[this_id, 'question'] = question
            df.loc[this_id, 'solution'] = str(prop_value).split("/")[-1]
            df.loc[this_id, 'entity_type'] = type
            df.loc[this_id, 'property'] = prop_name
    return question_list, solution_list, uuid_list, prop_list


def answer_questions(question_list, solution_list, unique_list, df, type):
    correct_count = 0
    total = len(question_list)
    index = 0
    tester = Tester()
    for question, this_id in zip(question_list, unique_list):
        print("Question: "+str(question))
        # resources = tester.get_resources(question)
        # df.loc[this_id, 'resources'] = resources
        answers = tester.get_answer(question)
        if len(answers) > 0:
            obtained_ans = answers[0]['answer']
            ans = str(obtained_ans).split(" .")[0]
            solution = str(solution_list[index]).split("/")[-1]
            confidence = str(answers[0]['confidence'])
            if str(ans).upper() == solution.upper():
                correct_count += 1
                log = "Correct: " + str(ans) + " equals " + solution
                print(log)
                print("Confidence: " + confidence)
                df.loc[this_id, 'correct'] = 'YES'
            elif solution.upper() in str(ans).upper():
                correct_count += 1
                log = "Correct: " + str(ans) + " includes the solution " + solution
                print(log)
                print("Confidence: " + confidence)
                df.loc[this_id, 'correct'] = 'YES (included)'
            else:
                log = "Incorrect: " + str(ans) + " not equals the solution " + solution
                print(log)
                print("Confidence: " + confidence)
                df.loc[this_id, 'correct'] = 'NO'
            index += 1
            df.loc[this_id, 'answer'] = str(ans)
            df.loc[this_id, 'confidence'] = confidence
        else:
            log = "No answer provided"
            print(log)
            index += 1
        df.loc[this_id, 'log'] = log

    final = "Questions finished. Correct: "+str(correct_count)+". Score: "+str(correct_count/total)
    print(final)
    df.loc['Results '+type, 'question'] = final


def answer_questions_from_dict(qa_dict, df):
    questions_list = [sublist[0] for sublist in list(qa_dict.values())]
    solutions_list = [sublist[1] for sublist in list(qa_dict.values())]
    props_list = [sublist[2] for sublist in list(qa_dict.values())]
    types_list = [sublist[3] for sublist in list(qa_dict.values())]
    uuid_list_dict = list(qa_dict.keys())
    unique_types = {}
    for q, a, u_id, p, t in zip(questions_list, solutions_list, uuid_list_dict, props_list, types_list):
        df.loc[u_id, 'question'] = q
        df.loc[u_id, 'solution'] = str(a).split("/")[-1]
        df.loc[u_id, 'entity_type'] = t
        df.loc[u_id, 'property'] = p
        if a == 'false' or a == 'true':
            df.loc[u_id, 'question_type'] = 'Boolean'
        else:
            df.loc[u_id, 'question_type'] = 'What'
        if t not in unique_types:
            unique_types[t] = []
        unique_types[t].append([q, a, u_id])
    for t in unique_types:
        aux_list = list(map(list, zip(*unique_types[t])))
        answer_questions(aux_list[0], aux_list[1], aux_list[2], df, t)


dataf = pd.DataFrame(columns=['question', 'solution', 'entity_type', 'question_type', 'property',
                              'answer', 'confidence', 'correct', 'log', 'resources'])

entity_types = ["Track", "Platform", "Siding", "ContactLineSystem",
                "TrainDetectionSystem", "ETCSLevel", "LineReference"]
labeled_types = ["OperationalPoint", "SectionOfLine"]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

qa_dict = {}
for t in entity_types:
    questions, solutions, uuid_list, prop_list = generate_questions(dataf, t)
    answer_questions(questions, solutions, uuid_list, dataf, t)
    for q, a, u_id, p in zip(questions, solutions, uuid_list, prop_list):
        qa_dict[u_id] = [q, a, p, t]

for t in labeled_types:
    questions, solutions, uuid_list, prop_list = generate_questions(dataf, t, labeled=True)
    answer_questions(questions, solutions, uuid_list, dataf, t)
    for q, a, u_id, p in zip(questions, solutions, uuid_list, prop_list):
        qa_dict[u_id] = [q, a, p, t]


json_data = json.dumps(qa_dict, ensure_ascii=False, indent=4)
with open(f'./qa_questions/qa_{timestamp}.json', 'w', encoding='utf8') as file:
    file.write(json_data)

file_name = f"./qa_reports/qa_report_{timestamp}.xlsx"
dataf.to_excel(excel_writer=file_name)

# # FROM JSON FILE
# with open(f'./qa_questions/qa_20230516_212503.json', 'r', encoding='utf8') as file:
#     qa_data = json.load(file)
#     answer_questions_from_dict(qa_data, dataf)
#     file_name = f"./qa_reports/qa_report_{timestamp}.xlsx"
#     dataf.to_excel(excel_writer=file_name)
