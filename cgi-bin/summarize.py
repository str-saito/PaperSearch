#!/usr/local/bin/python

import sys
import os
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '../util'))

import cgi
import cgitb
import markdown
from text_summarization import PaperSummarizer
from dotenv import load_dotenv

cgitb.enable()
load_dotenv()
print("Content-Type: text/html\n")

form = cgi.FieldStorage()
paper_id = form.getvalue("paper_id")

if paper_id:
    try:
        summarizer = PaperSummarizer()
        full_text = summarizer.get_paper_from_db(paper_id)

        if full_text:
            summary = summarizer.summarize_text(full_text)
            fmt_summary = markdown.markdown(summary)
            fmt_summary = re.sub(r'<h[1-6]>(.*?)</h[1-6]>', r'<p><strong>\1</strong></p>', fmt_summary)
            print(f"<p>{fmt_summary}</p>")
        else:
            print("Paper not found.")
    except Exception as e:
        print(f"<p>要約に失敗しました: {e}</p>")
else:
    print("<p>無効なリクエストです。</p>")
