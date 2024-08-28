import os
import pymysql
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv()

db_conn = pymysql.connect(
    host = os.getenv('MYSQL_HOST'),
    user = os.getenv('MYSQL_USER'),
    password = os.getenv('MYSQL_PASSWORD'),
    database = os.getenv('MYSQL_DATABASE')
)

es_host = os.getenv('ES_HOST')
es_port = int(os.getenv('ES_PORT'))

host = f'http://{es_host}:{es_port}'
client = Elasticsearch(hosts=[host])

embedding = HuggingFaceEmbeddings(model_name='intfloat/multilingual-e5-large')

def create_index(index_name):
    if not client.indices.exists(index=index_name):
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
        client.indices.create(index=index_name, body=mapping)
        print(f"Created index with mapping: {index_name}")

def get_papers_from_db():
    with db_conn.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT id, title, abstract, full_text FROM papers")
        return cursor.fetchall()

def index_elasticsearch(papers):
    for paper in papers:
        title_vector = embedding.embed_query(paper['title'])
        abstract_vector = embedding.embed_query(paper['abstract'])
        full_text_vector = embedding.embed_query(paper['full_text'])

        doc = {
            "title_vector": title_vector,
            "abstract_vector": abstract_vector,
            "full_text_vector": full_text_vector,
            "metadata": {"id": paper['id']}
        }
        client.index(index="papers", body=doc)
    
    print(f"Indexed {len(papers)} documents.")

def search_elasticsearch(query_text):
    query_vector = embedding.embed_query(query_text)
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                # いったんはインデックスしたすべての情報を使って検索をかけている
                # 多分全文検索とミックスした方が精度がよくなると思う
                "source": "cosineSimilarity(params.query_vector, 'title_vector') + cosineSimilarity(params.query_vector, 'abstract_vector') + cosineSimilarity(params.query_vector, 'full_text_vector')",
                "params": {"query_vector": query_vector}
            }
        }
    }
    
    response = client.search(index="papers", body={"query": script_query, "size": 10})
    return response['hits']['hits']

def main(query_text):
    create_index('papers')
    papers = get_papers_from_db()
    index_elasticsearch(papers)
    es_results = search_elasticsearch(query_text)
    print("Top 10 Search Results:")
    for result in es_results:
        print(f"ID: {result['_source']['metadata']['id']}")
        print(f"Score: {result['_score']}")
        print("----------")

# ToDO cgi-bin/paperserch.pyの時は検索ボタンを押してクエリに対して検索結果を返すようにする
query_text = "Transformer"
main(query_text)

db_conn.close()
