#!/usr/local/bin/python

import os
import http.cookies as Cookie
import pymysql
import cgitb

cgitb.enable()

def connect_db():
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', '192.168.11.135'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )

def logout():
    cookie = Cookie.SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
    session_id = cookie.get('session_id')

    if session_id is not None:
        session_id = session_id.value
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = %s", (session_id,))
        connection.commit()
        connection.close()
    cookie['session_id'] = ''
    cookie['session_id']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    print("Content-Type: text/html")
    print("Content-Type: text/html; charset=utf-8\n")
    print('<meta http-equiv="refresh" content="0;URL=/">')
    print()

if __name__ == "__main__":
    logout() 
