import pprint
from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import scan, bulk
import json


class Connection:

    # "labels_index"
    # "abstractions_index"
    def __init__(self):
        self.es = Elasticsearch("http://localhost:9200")
        # print(self.es.info())
        self.index_name = "labels_index"
        # with open('../abstractions.json', 'r', encoding='utf8') as file:
        # with open('../uopid.json', 'r', encoding='utf8') as file:
        # with open('../specials.json', 'r', encoding='utf8') as file:
        # with open('../line_references.json', 'r', encoding='utf8') as file:
        # with open('../merged.json', 'r', encoding='utf8') as file:
        # with open('../no_ascii_merged.json', 'r', encoding='utf8') as file:

    def generate_docs(self):
        with open('../labels.json', 'r', encoding='utf8') as file:
            js = json.load(file)
            for key, value in js.items():
                doc = {
                    "_index": self.index_name,
                    "_source": {
                        "label": key,
                        "uris": [value]
                    }
                }
                yield doc
        print("Finished ingesting index")

    def delete_all_docs(self):
        batch_size = 1000
        query = {
            "query": {
                "match_all": {}
            }
        }
        docs = scan(self.es, index=self.index_name, query=query)
        while True:
            # Get the next batch of documents
            batch = [doc["_id"] for _, doc in zip(range(batch_size), docs)]
            if not batch:
                # No more documents to delete
                print("No batch")
                break
            # Delete the documents in the batch
            res = bulk(self.es, [{"_op_type": "delete", "_index": self.index_name, "_id": doc_id} for doc_id in batch])
            print(res)

    def generate_query(self, user_label):
        search_query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "label": user_label
                            }
                        },
                        {
                            "match": {
                                "label": {
                                    "query": user_label,
                                    "operator": "and",
                                    "fuzziness": "0"
                                }
                            }
                        },
                        {
                            "fuzzy": {
                                "label": {
                                    "value": user_label,
                                    "fuzziness": "AUTO"
                                }
                            }
                        }
                    ]}}}
        # pprint.pprint(self.es.search(index=self.index_name, body=search_query))
        return self.es.search(index=self.index_name, body=search_query)


# user_label = "Guadalajara"
        # FIRST VERSION
        # search_query = {
        #     "query": {
        #         "match": {
        #             "label": user_label
        #         }
        #     }
        # }

# con = Connection()

# res = helpers.bulk(con.es, con.generate_docs(), request_timeout=30)
# print(res)
#
# res = con.es.count(index=con.index_name, request_timeout=30)
# print(res)

# elastic_result = con.generate_query("track 1670_BEMHLG_1395-1_BEMH")
# pprint.pprint(elastic_result)
# for doc_elem in elastic_result['hits']['hits']:
#     print(doc_elem['_source']['label'])

# # # # # ### con.delete_all_docs()
