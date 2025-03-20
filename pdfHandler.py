from PyPDF2 import PdfReader
import io
import requests
from bs4 import BeautifulSoup

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