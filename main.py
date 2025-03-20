#/////////////////////////////////////////// 
#//
#// Application to generate "手球賽裁判記錄表"
#// Author: Wong Tsz Ho
#// 
#/////////////////////////////////////////// 

from match_data import extract_matches_for_date, display_matches
from ref_data import *
from documentation import *
from pdfHandler import *
import sys
from datetime import datetime

def parse_date(date_str):
    try:
        # Convert input date string to datetime object
        return datetime.strptime(date_str, '%d/%m/%Y')
    except ValueError:
        print("Invalid date format. Please use DD/MM/YYYY")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python exe.py DD/MM/YYYY")
        sys.exit(1)
    
    # Parse target date
    target_date = parse_date(sys.argv[1])
    
    # Store referee number
    referees = sys.argv[2:]
    
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Download and read PDF
    url_league = "https://www.handball.org.hk/2_Competition/2024-2025/聯賽/(92) 2024_LAEGUE_TIMETABLE_2025.03.18.pdf"
    url_spring_cup = "http://www.handball.org.hk/2_Competition/2024-2025/%E6%89%8B%E7%B8%BD%E7%9B%83/(4)%202024_%E6%89%8B%E7%B8%BD%E7%9B%83%E8%B3%BD%E7%A8%8B_2025.03.20.pdf"
    url_ref = "http://www.handball.org.hk/6_Referee/2024-2025/2024-2025%E8%A3%81%E5%88%A4%E5%90%8D%E5%96%AE_20250226.pdf"
    content = download_and_read_pdf(url_league)
    ref_content = download_and_read_pdf(url_ref)
    
    if not content:
        print("Failed to read match PDF content")
        sys.exit(1)
    else:
        print("Match PDF content read successfully")
        update_txt_file(content, 'output.txt')       
        
    if not ref_content:
        print("Failed to read referee PDF content")
        sys.exit(1)
    else:
        print("Referee PDF content read successfully")
        update_txt_file(ref_content, 'ref_output.txt')
    
    # Extract and display matches
    matches = extract_matches_for_date(content, target_date)
    display_matches(matches)
    
    # Extract and display referees (if have)
    refs = []
    if referees:
        refs = extract_referees(ref_content, referees)
        display_referee(refs)
    
    # Path to the template file
    template_path = "data/聯賽比賽記錄表_template.docx"

    # Create the new .docx file
    create_docx_from_template(template_path, matches, refs)

if __name__ == "__main__":
    main()
