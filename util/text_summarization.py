import os
import pymysql
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

class PaperSummarizer:
    def __init__(self):
        self.db_conn = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        )
        self.genai_api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.genai_api_key)

    def get_paper_from_db(self, paper_id):
        with self.db_conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT full_text FROM papers WHERE id = %s", (paper_id,))
            result = cursor.fetchone()
            return result['full_text'] if result else None

    def summarize_text(self, sentence):
        prompt = f"""
        You are a professional summarizer. Your task is to create a structured and concise summary of the following research paper. 
        Please output the summary in a format that is suitable for HTML display. Each section should be enclosed in <p> tags.

        # Summary Format:
        - **Introduction:** A brief overview of the main topic and problem addressed by the paper.
        - **Method:** A concise description of the approach or methodology used in the paper.
        - **Contributions:** Highlight the key contributions made by the paper.
        - **Results:** Summarize the main findings and results presented in the paper.
        - **Importance:** Explain the significance and potential impact of the paper's findings.

        # Output Example:
        <p><strong>Introduction:</strong> [Your summary here]</p>
        <p><strong>Method:</strong> [Your summary here]</p>
        <p><strong>Contributions:</strong> [Your summary here]</p>
        <p><strong>Results:</strong> [Your summary here]</p>
        <p><strong>Importance:</strong> [Your summary here]</p>

        # Please use this format:
        {sentence}
        """
        gemini_pro = genai.GenerativeModel("gemini-pro")
        response = gemini_pro.generate_content(prompt)
        return response.text
    