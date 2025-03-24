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

def get_latest_pdf_url():
    # URL of the competition page
    competition_url = "http://www.handball.org.hk/competition.htm"
    
    # Fetch the page content
    response = requests.get(competition_url)
    response.raise_for_status()  # Raise an error for bad responses

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the relevant links
    # Adjust the selector according to the actual structure of the HTML
    pdf_links = soup.find_all('a', string=lambda text: 'pdf' in text.lower())
    
    # Assuming the first link is the latest PDF based on your needs
    if pdf_links:
        latest_pdf_url = pdf_links[10]['href']
        # Ensure the URL is absolute
        if not latest_pdf_url.startswith('http'):
            latest_pdf_url = f"http://www.handball.org.hk/{latest_pdf_url}"
        return latest_pdf_url
    else:
        return None

# Example usage
latest_pdf_url = get_latest_pdf_url()
if latest_pdf_url:
    print(f"The latest PDF URL is: {latest_pdf_url}")
    # Now you can download and read the PDF
    #content = download_and_read_pdf(latest_pdf_url)
else:
    print("No PDF link found.")