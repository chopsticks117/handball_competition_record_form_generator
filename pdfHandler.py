from PyPDF2 import PdfReader
import io
import requests

def download_and_read_pdf(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/pdf,*/*'
        }
        
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        pdf_file = io.BytesIO(response.content)
        pdf_reader = PdfReader(pdf_file)
        
        # Extract text from all pages
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text()
            
        return text_content
    except Exception as e:
        print(f"Error: {e}")
        return None
