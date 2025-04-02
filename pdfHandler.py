from PyPDF2 import PdfReader
import io
import requests
from bs4 import BeautifulSoup
import pdfplumber

def download_and_read_pdf(url, match_type):
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/pdf,*/*'
        }
        
        # Download the PDF
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        # Load the PDF from the response content
        pdf_file = io.BytesIO(response.content)
        
        if match_type != "聯賽":
            return read_by_pdfplumber(pdf_file)
        else:
            return read_by_PdfReader(pdf_file)
        
    except requests.exceptions.RequestException as req_err:
        print(f"Request error: {req_err}")
        return None
    except Exception as e:
        print(f"General error: {e}")
        return None
    
def read_by_pdfplumber(pdf_file):
    try:
        # Extract text using pdfplumber
        text_content = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page_number, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:  # Check if text extraction was successful
                        text_content += page_text + "\n"  # Add new line for separation
                    else:
                        print(f"No text found on page {page_number + 1}")
                except Exception as e:
                    print(f"Error reading page {page_number + 1}: {e}")

        return text_content.strip()  # Return trimmed text content
    
    except requests.exceptions.RequestException as req_err:
        print(f"Request error: {req_err}")
        return None
    except Exception as e:
        print(f"General error: {e}")
        return None

def read_by_PdfReader(pdf_file):
    try:
        
        pdf_reader = PdfReader(pdf_file)
        
        # Extract text from all pages
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text()
            
        return text_content
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_latest_league_pdf_url():
    # Base URL for the PDF
    base_url = "http://www.handball.org.hk/2_Competition/2024-2025/%E8%81%AF%E8%B3%BD/(95)%202024_LAEGUE_TIMETABLE_"
    
    # Start from today's date
    today = datetime.now()
    
    while True:
        # Format the date to match the required format in the URL
        date_str = today.strftime("%Y.%m.%d")
        pdf_url = f"{base_url}{date_str}.pdf"
        
        # Check if the PDF exists
        response = requests.head(pdf_url)
        
        if response.status_code == 200:
            # PDF found
            return pdf_url
        
        # Move to the previous day
        today -= timedelta(days=1)

def get_latest_ref_pdf_url():
    # Base URL for the PDF
    base_url = "http://www.handball.org.hk/6_Referee/2025-2026/2025-2026%E8%A3%81%E5%88%A4%E5%90%8D%E5%96%AE_"
    
    # Start from today's date
    today = datetime.now()
    
    while True:
        # Format the date to match the required format in the URL
        date_str = today.strftime("%Y%m%d")
        pdf_url = f"{base_url}{date_str}.pdf"
        
        # Check if the PDF exists
        response = requests.head(pdf_url)
        
        if response.status_code == 200:
            # PDF found
            return pdf_url
        
        # Move to the previous day
        today -= timedelta(days=1)

if debug:
    latest_league_pdf = get_latest_league_pdf_url()
    latest_ref_pdf = get_latest_ref_pdf_url()
    print(f"Latest League PDF URL: {latest_league_pdf}")
    print(f"Latest Referee PDF URL: {latest_ref_pdf}")
