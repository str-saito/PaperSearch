#!/usr/local/bin/python

import cgi
import cgitb
import pymysql
import hashlib
import os
import http.cookies as Cookie
import uuid

cgitb.enable()

def render_login_html(message=""):
    print("Content-Type: text/html\n")
    print(f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>PaperSearch ログイン</title>
            <link rel="stylesheet" href="http://192.168.11.135:8000/static/css/styles.css">
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css">
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
        </head>
        <body>
            <header>
                <nav>
                    <div class="logo"><a href="/" class="logo-link">PaperSearch</a></div>
                    <div class="nav-links">
                    </div>
                </nav>
            </header>
            <main>
                <div class="login-container">
                    <h2 class="text-center">ログイン</h2>
                    <form action="/login" method="post">
                        <div class="form-group">
                            <label for="username">ユーザー名</label>
                            <input type="text" id="username" name="username" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label for="password">パスワード</label>
                            <input type="password" id="password" name="password" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-primary form-group">送信</button>
                    </form>
                    <p>ユーザーの新規作成がまだの方は<a href="/register">こちら</a></p>
                    <p>{message}</p>
                </div>
            </main>
            <footer>
                <div class="footer-content">
                    <p></p>
                    <ul>
                        <li>✔ 論文の検索をすることが可能</li>
                        <li>✔ ログインで論文の要約が可能</li>
                    </ul>
                </div>
            </footer>
            <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js"></script>
        </body>

        </html>

    """)

def connect_db():
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', '192.168.11.135'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )

def get_user_by_username(connection, username):
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    return cursor.fetchone()

def verify_password(stored_password, provided_password):
    provided_password_hash = hashlib.sha256(provided_password.encode()).hexdigest()
    return stored_password == provided_password_hash

def create_session(connection, user_id):
    session_id = str(uuid.uuid4())
    cursor = connection.cursor()
    cursor.execute("INSERT INTO sessions (session_id, user_id) VALUES (%s, %s)", (session_id, user_id))
    connection.commit()
    return session_id

def set_session_cookie(session_id):
    cookie = Cookie.SimpleCookie()
    cookie['session_id'] = session_id
    cookie['session_id']['path'] = '/'
    print(cookie.output())

try:
    form = cgi.FieldStorage()
    username = form.getvalue("username")
    password = form.getvalue("password")

    if username and password:
        connection = connect_db()
        user = get_user_by_username(connection, username)
        
        if user and verify_password(user['password_hash'], password):
            session_id = create_session(connection, user['id'])
            set_session_cookie(session_id)
            print("Content-Type: text/html; charset=utf-8\n")
            print('<meta http-equiv="refresh" content="0;URL=/">')
        else:
            render_login_html("ユーザー名またはパスワードが間違っています。")
    else:
        render_login_html()

except Exception as e:
    print("Content-Type: text/html\n")
    print(f"<p>エラーが発生しました: {e}</p>")

finally:
    if 'connection' in locals():
        connection.close()
