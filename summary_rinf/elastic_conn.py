import pprint
from elasticsearch import Elasticsearch, helpers
import json


class Connection:

    # "labels_index"
    # "abstractions_index"
    def __init__(self):
        self.es = Elasticsearch("http://localhost:9200")
        # print(self.es.info())
        self.index_name = "labels_index"

    def generate_docs(self):
        # with open('../labels.json', 'r', encoding='utf8') as file:
        with open('../abstractions.json', 'r', encoding='utf8') as file:
            js = json.load(file)
            id = 0
            for key, value in js.items():
                doc = {
                    "_index": self.index_name,
                    "_id": id,
                    "_source": {
                        "id": id,
                        "label": key,
                        "uris": [value]
                    }
                }
                id = id + 1
                yield doc
        print("Finished ingesting index")

    def generate_query(self, user_label):
        # user_label = "Guadalajara"
        search_query = {
            "query": {
                "match": {
                    "label": user_label
                }
            }
        }
        # pprint.pprint(self.es.search(index=self.index_name, body=search_query))
        return self.es.search(index=self.index_name, body=search_query)


# con = Connection()
# # res = helpers.bulk(con.es, con.generate_docs(), request_timeout=30)
# # print(res)
# #
# # res = con.es.count(index=con.index_name, request_timeout=30)
# # print(res)
#
# elastic_result = con.generate_query("track 3572-DE0FOHF-single-track-DE0FWOI")
# # pprint.pprint(elastic_result)
# for doc_elem in elastic_result['hits']['hits']:
#     print(doc_elem['_source']['label'])
