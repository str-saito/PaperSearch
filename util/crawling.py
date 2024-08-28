import os
import requests
from bs4 import BeautifulSoup
import fitz
import pymysql
from dotenv import load_dotenv


load_dotenv()

class PaperProcessor:
    def __init__(self):
        self.db_conn = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        )

    def download_pdf(self, url, local_path):
        response = requests.get(url)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            f.write(response.content)

    def clean_text(self, text):
        lines = text.splitlines()
        cleaned_lines = []
        for i in range(len(lines)):
            if i > 0 and lines[i-1].endswith('-') and lines[i].startswith(' '):
                cleaned_lines[-1] = cleaned_lines[-1][:-1] + lines[i].strip()
            else:
                cleaned_lines.append(lines[i])
        return ' '.join(cleaned_lines)

    def format_text(self, text):
        return self.clean_text(text)

    def extract_abstract(self, text):
        start_keyword = "Abstract"
        end_keywords = ["1.", "Introduction", "I. "]

        start_idx = text.find(start_keyword)
        if start_idx == -1:
            return "Abstract not found"

        end_idx = len(text)
        for end_keyword in end_keywords:
            end_idx_temp = text.find(end_keyword, start_idx + len(start_keyword))
            if end_idx_temp != -1:
                end_idx = min(end_idx, end_idx_temp)

        abstract = text[start_idx + len(start_keyword):end_idx].strip()
        return abstract

    def save_db(self, title, abstract, authors, full_text, journal, full_text_url):
        with self.db_conn.cursor() as cursor:
            sql = """
            INSERT INTO papers (title, abstract, authors, full_text, journal, full_text_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (title, abstract, authors, full_text, journal, full_text_url))
        self.db_conn.commit()

    def process_papers(self, url):
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        paper_items = soup.select("#content > dl > dd:nth-child(3n+4) > a:nth-child(1)")

        for item in paper_items:
            pdf_url = f"https://openaccess.thecvf.com{item.get('href')}"
            local_pdf_path = "temp_paper.pdf"
            self.download_pdf(pdf_url, local_pdf_path)
            doc = fitz.open(local_pdf_path)
            title = doc.metadata.get('title', 'No Title')
            authors = doc.metadata.get('author', 'No Author')
            journal = "CVPR 2024"

            full_text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                formatted_text = self.format_text(text)
                full_text += formatted_text
            abstract = self.extract_abstract(full_text)
            self.save_db(title, abstract, authors, full_text, journal, pdf_url)

            os.remove(local_pdf_path)

    def close_connection(self):
        self.db_conn.close()
