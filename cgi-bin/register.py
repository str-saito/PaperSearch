#!/usr/local/bin/python

import cgi
import cgitb
import pymysql
import hashlib
import os
from http import HTTPStatus

cgitb.enable()
print("Content-Type: text/html\n")

form = cgi.FieldStorage()
username = form.getvalue("username")
email = form.getvalue("email")
password = form.getvalue("password")
confirm_password = form.getvalue("confirm_password")


def render_registration_html(message=""):
    print(f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css">
        <link rel="stylesheet" href="http://192.168.11.135:8000/static/css/styles.css">
        <title>PaperSearch 新規会員登録</title>
    </head>
    <header>
        <nav>
            <div class="logo"><a href="/" class="logo-link">PaperSearch</a></div>
            <div class="nav-links"></div>
        </nav>
    </header>
    <body class="bg-light">
        <div class="register-container">
            <h2 class="text-center">新規会員登録</h2>
            <form action="/register" method="post">
                <div class="form-group">
                    <label for="username">ユーザー名</label>
                    <input type="text" id="username" name="username" class="form-control" required>
                </div>
                <div class="form-group">
                    <label for="email">メールアドレス</label>
                    <input type="email" id="email" name="email" class="form-control" required>
                </div>
                <div class="form-group">
                    <label for="password">パスワード</label>
                    <input type="password" id="password" name="password" class="form-control" required>
                </div>
                <div class="form-group">
                    <label for="confirm_password">パスワード確認</label>
                    <input type="password" id="confirm_password" name="confirm_password" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary form-group">登録</button>
            </form>
            <p>すでにアカウントをお持ちの方は<a href="/login">こちら</a></p>
            <p>{message}</p>
        </div>
        <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js"></script>
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
    """)

def connect_db():
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', '192.168.11.135'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_exist_user(connection, username, email):
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
    return cursor.fetchone() is not None

def create_user(connection, username, email, password_hash):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", 
                   (username, email, password_hash))
    connection.commit()

try:
    if not username or not email or not password or not confirm_password:
        render_registration_html()
    else:
        connection = connect_db()

        if password != confirm_password:
            raise ValueError("パスワードが一致しません。")

        if is_exist_user(connection, username, email):
            raise ValueError("このユーザー名またはメールアドレスは既に使用されています。")

        password_hash = hash_password(password)
        create_user(connection, username, email, password_hash)
        
        print("Content-Type: text/html; charset=utf-8\n")
        print('<meta http-equiv="refresh" content="0;URL=/login">')

except ValueError as ve:
    render_registration_html(str(ve))

except pymysql.MySQLError as e:
    print("<html><head><meta charset='utf-8'><title>エラー</title></head><body>")
    print(f"<p>Mysqlでエラー: {e}</p>")
    print("</body></html>")

finally:
    if 'connection' in locals():
        connection.close()
