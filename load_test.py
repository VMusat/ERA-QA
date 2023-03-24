import pyoxigraph as po
from pyoxigraph import Store

input = fr'.\filtered-rinferatv.nq'
type = 'application/n-quads'
store = Store(path="./graph")

store.bulk_load(input, type)

# ans = store.named_graphs()
# for name in ans:
#     print(name)
#     file = open(str(name).split("http://data.europa.eu/949/graph/")[1].rstrip(">")+".nt", 'wb')
#     store.dump(file, mime_type="application/n-triples", from_graph=name)
#     for solution in store.query(
#             'SELECT ?prop (count(?prop) as ?propTotal) WHERE { ?s ?prop ?o } GROUP BY ?prop ORDER BY ASC(?propTotal)',
#             default_graph=name):
#         print(solution)
# print('Default Graph')
# file = open("defaultGraph.nt", 'wb')
# store.dump(file, mime_type="application/n-triples")
# for solution in store.query(
#         'SELECT ?prop (count(?prop) as ?propTotal) WHERE { ?s ?prop ?o } GROUP BY ?prop ORDER BY ASC(?propTotal)'):
#     print(solution)




