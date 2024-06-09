
from elasticsearch import Elasticsearch
import json
from pprint import pprint
import os
import time
import re


from dotenv import load_dotenv
load_dotenv()
esuser = os.getenv("ESUSER")
espassword = os.getenv("ESPASSWORD")
eshost = os.getenv("ESHOST")
esport = os.getenv("ESPORT")
# es_ssl_fingerprint = !openssl s_client -connect $eshost:$esport  -showcerts </dev/null 2>/dev/null | openssl x509 -fingerprint -sha256 -noout -in /dev/stdin
# es_ssl_fingerprint = es_ssl_fingerprint[0].split("=")[1]

class Search:
    def __init__(self):
        self.es_client = Elasticsearch(
            f'https://{eshost}:{esport}',
            basic_auth=(esuser, espassword),
            verify_certs=False,
            request_timeout=3600,
            # ssl_assert_fingerprint=es_ssl_fingerprint
            )  
        client_info = self.es_client.info()
        print('Connected to Elasticsearch!')
        pprint(client_info.body)
        self.model_id = '.elser_model_2'
    
    def extract_filters(self, query):
        filters = []
        filter_regex = r'category:([^\s]+)\s*'
        m = re.search(filter_regex, query)
        if m:
            filters.append({
                'term': {
                    'category.keyword': {
                        'value': m.group(1)
                    }
                }
            })
        query = re.sub(filter_regex, '', query).strip()
        return {'filter': filters}, query

    def handle_search(self, query, size=5, min_score=8):
        es = self.es_client
        filters, parsed_query = self.extract_filters(query)
        results = es.search(
            index = 'my_documents1',
            query={
                'bool': {
                    'must': [
                        {
                            'text_expansion': {
                                'elser_embedding': {
                                    'model_id': '.elser_model_2',
                                    'model_text': parsed_query,
                                }
                            },
                        }
                    ],
                    **filters,
                }
            },
            aggs={
                'category-agg': {
                    'terms': {
                        'field': 'category.keyword',
                    }
                },
                'year-agg': {
                    'date_histogram': {
                        'field': 'updated_at',
                        'calendar_interval': 'year',
                        'format': 'yyyy',
                    },
                },
            },
            size = size,
            min_score = min_score
        )
        results = results['hits']['hits']
        return [[hit['_source']['page_content'], hit['_source']['metadata']['source'], hit['_score']] for hit in results]

        
# parsed_query = "how do i book an appointment?"
# response = self.es_client.search(
#         index='my_documents', 
#         body={
#             'query': {
#                 'bool': {
#                     'must': [
#                         {
#                             'text_expansion': {
#                                 'elser_embedding': {
#                                     'model_id': self.model_id,
#                                     'model_text': parsed_query,
#                                 }
#                             },
#                         }
#                     ],
#                 }
#             },
#             'aggs': {
#                 'category-agg': {
#                     'terms': {
#                         'field': 'category.keyword',
#                     }
#                 },
#             },
#             'size': 5,
#             "min_score": 8 ,
#         },
#     )