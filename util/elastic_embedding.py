import os
import pymysql
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv()

class ServeElasticsearch:
    def __init__(self):
        self.db_conn = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        )
        
        es_host = os.getenv('ES_HOST')
        es_port = int(os.getenv('ES_PORT'))
        host = f'http://{es_host}:{es_port}'
        self.client = Elasticsearch(hosts=[host])
        self.embedding = HuggingFaceEmbeddings(model_name='intfloat/multilingual-e5-large')

    def create_index_for_elasticsearch(self, index_name):
        if not self.client.indices.exists(index=index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "title_vector": {
                            "type": "dense_vector",
                            "dims": 1024
                        },
                        "abstract_vector": {
                            "type": "dense_vector",
                            "dims": 1024
                        },
                        "full_text_vector": {
                            "type": "dense_vector",
                            "dims": 1024
                        }
                    }
                }
            }
            self.client.indices.create(index=index_name, body=mapping)
            print(f"Created index with mapping: {index_name}")

    def get_papers_from_db(self, paper_ids):
        format_strings = ','.join(['%s'] * len(paper_ids))
        
        query = f"SELECT id, title, abstract FROM papers WHERE id IN ({format_strings})"
        
        with self.db_conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query, tuple(paper_ids))
            return cursor.fetchall()


    def index_elasticsearch(self, papers):
        for paper in papers:
            title_vector = self.embedding.embed_query(paper['title'])
            abstract_vector = self.embedding.embed_query(paper['abstract'])
            full_text_vector = self.embedding.embed_query(paper['full_text'])

            doc = {
                "title_vector": title_vector,
                "abstract_vector": abstract_vector,
                "full_text_vector": full_text_vector,
                "metadata": {"id": paper['id']}
            }
            self.client.index(index="papers", body=doc)
        
        print(f"Indexed {len(papers)} documents.")

    def search_elasticsearch(self, query_text):
        """
        いったんはインデックスしたすべての情報を使って検索をかけている
        多分全文検索とミックスした方が精度がよくなると思う
        """
        query_vector = self.embedding.embed_query(query_text)
        script_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'title_vector') + cosineSimilarity(params.query_vector, 'abstract_vector') + cosineSimilarity(params.query_vector, 'full_text_vector')",
                    "params": {"query_vector": query_vector}
                }
            }
        }
        response = self.client.search(index="papers", body={"query": script_query, "size": 10})
        return response['hits']['hits']

    def close_db_connection(self):
        self.db_conn.close()