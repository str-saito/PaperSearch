#!/usr/local/bin/python

print("Content-Type: text/html\n") 

print("""
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
        <div class="container mt-5">
            ページが見つかりませんでした。<br>
            そのページは既に存在しないか、URL が誤っている可能性があります。<br>
            <a href="/">PaperSearch トップへ</a>
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
