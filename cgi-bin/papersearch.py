#!/usr/local/bin/python

import sys
import os

os.environ['HF_HOME'] = '/app/cache/huggingface'
sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))

import cgi
import cgitb
import http.cookies as Cookie
import pymysql
from dotenv import load_dotenv
from paper_search import PaperSearchService


cgitb.enable()
load_dotenv()
print("Content-Type: text/html\n")

form = cgi.FieldStorage()
keyword = form.getvalue("keyword")

def render_search_html():
    username = is_logged_in()
    if username:
        login_link = f'<a>{username} さん</a><a href="/logout">ログアウト</a>'
        message = ""
    else:
        login_link = '<a href="/login">ログイン</a>'
        message = """
            <div class="alert alert-warning" role="alert" style="text-align: center;">
                要約機能を使用するには<a href="/login">ログイン</a>をしてください。
            </div>
            """

    return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>PaperSearch</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css">
    <link rel="stylesheet" href="http://192.168.11.135:8000/static/css/styles.css">
    
</head>
<body class="bg-light">
    <header>
        <nav>
            <div class="logo"><a href="/" class="logo-link">PaperSearch</a></div>
            <div class="nav-links">
                {login_link}
            </div>
        </nav>
    </header>
    {message}
    <div class="container mt-5">
        <h1 class="text-center">論文検索</h1>
        <form id="search-form" class="form-inline justify-content-center my-4">
            <div class="form-group mx-sm-3 mb-2 col-md-6">
                <label class="mr-3">カンファレンス:</label>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="conference" id="cvpr2024" value="CVPR2024" checked="checked">
                    <label class="form-check-label" for="cvpr2024">CVPR2024</label>
                </div>
            </div>
            <div class="form-group mx-sm-3 mb-2 col-md-6">
                <label for="keyword" class="sr-only">検索キーワード</label>
                <input type="text" id="keyword" name="keyword" class="form-control keyword-input w-100" placeholder="キーワードを入力" required>
            </div>

            <button type="submit" class="btn btn-primary mb-2 w-auto">検索</button>
        </form>
        <div id="results"></div>
    </div>

    <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js"></script>
    <script src="http://192.168.11.135:8000/static/js/search.js"></script>
</body>
<footer>
    <div class="footer-content">
        <p></p>
        <ul>
            <li>✔ 論文の検索をすることが可能</li>
            <li>✔ ログインで論文の要約が可能</li>
        </ul>
    </div>
</footer>
</html>
    """

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
        cursor.execute(
            """
                SELECT users.username FROM sessions 
                JOIN users ON sessions.user_id = users.id 
                WHERE sessions.session_id = %s
            """,
            (session_id,)
        )
        session = cursor.fetchone()
        connection.close()

        if session:
            return session['username']
    return None

if not keyword:
    print(render_search_html())
else:
    service = PaperSearchService()
    result_html = service.search_papers(keyword)
    print(result_html)