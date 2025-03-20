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
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

def parse_date(date_str):
    try:
        # Convert input date string to datetime object
        return datetime.strptime(date_str, '%d/%m/%Y')
    except ValueError:
        raise ValueError("Invalid date format. Please use DD/MM/YYYY")

def run_application(target_date, referees):
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
        raise Exception("Failed to read match PDF content")
    
    if not ref_content:
        raise Exception("Failed to read referee PDF content")

    # Extract and display matches
    matches = extract_matches_for_date(content, target_date)
    if not matches:
        raise Exception("No matches found for the specified date")
    else:
        display_matches(matches)

    # Extract and display referees (if any)
    refs = []
    if referees:
        refs = extract_referees(ref_content, referees)
        display_referee(refs)

    # Path to the template file
    template_path = "/Users/tszhowong/Desktop/Handball/Referee/Application/data/聯賽比賽記錄表_template.docx"

    # Create the new .docx file
    create_docx_from_template(template_path, matches, refs)
    messagebox.showinfo("Success", "Document generated successfully!")

def start_application():
    target_date = date_entry.get()
    referees = referee_entry.get().split(',')

    try:
        parsed_date = parse_date(target_date)
        run_application(parsed_date, referees)
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Setting up the UI with Tkinter
root = tk.Tk()
root.title("手球賽裁判記錄表生成器")

# Input for date
tk.Label(root, text="Match Date (DD/MM/YYYY):").pack(pady=5)
date_entry = tk.Entry(root)
date_entry.pack(pady=5)

# Input for referees
tk.Label(root, text="Referee Numbers (comma-separated):").pack(pady=7)
referee_entry = tk.Entry(root)
referee_entry.pack(pady=5)

# Generate button
generate_button = tk.Button(root, text="Generate Document", command=start_application)
generate_button.pack(pady=20)

# Run the application
root.mainloop()