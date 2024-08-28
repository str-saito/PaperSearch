import sys
import os

os.environ['HF_HOME'] = '/app/cache/huggingface'
sys.path.append(os.path.join(os.path.dirname(__file__), './util'))
from elastic_embedding import ServeElasticsearch
import pymysql
import http.cookies as Cookie

class PaperSearchService:
    def __init__(self):
        self.es_service = ServeElasticsearch()

    def search_papers(self, keyword):
        try:
            search_results = self.es_service.search_elasticsearch(keyword)
            
            if search_results:
                paper_ids = [result['_source']['metadata']['id'] for result in search_results]
                query_results = self.es_service.get_papers_from_db(paper_ids)
                
                result_html = self.generate_results_html(query_results)
                return result_html
            else:
                return '<p>No results found.</p>'
        
        except Exception as e:
            return f"<p>エラーが発生しました: {e}</p>"
        
        finally:
            self.es_service.close_db_connection()

    def generate_results_html(self, query_results):
        def connect_db():
            return pymysql.connect(
                host=os.getenv('MYSQL_HOST', '192.168.11.135'),
                port=int(os.getenv('MYSQL_PORT', 3306)),
                user=os.getenv('MYSQL_USER'),
                password=os.getenv('MYSQL_PASSWORD'),
                database=os.getenv('MYSQL_DATABASE')
            )

        def is_logged_in():
            cookie = Cookie.SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
            session_id = cookie.get('session_id')

            if session_id is not None:
                session_id = session_id.value
                connection = connect_db()
                cursor = connection.cursor(pymysql.cursors.DictCursor)
                cursor.execute("SELECT * FROM sessions WHERE session_id = %s", (session_id,))
                session = cursor.fetchone()
                connection.close()

                if session:
                    return True
            return False
        
        result_html = '<div class="list-group">'
        for query_result in query_results:
            paper_id = query_result['id']
            title = query_result['title']
            abstract = query_result['abstract']
            result_html += '<div class="list-group-item">'
            result_html += f'<h4 class="mb-1">{title}</h4>'
            result_html += f'<p><strong>Abstract:</strong> {abstract}</p>'
            if is_logged_in():
                result_html += f'<p><a href="#" class="summarize-link" data-paper-id="{paper_id}">要約する</a></p>'
                result_html += f'<div id="summary_{paper_id}"></div>'
            result_html += '</div>'
        result_html += '</div>'
        return result_html
