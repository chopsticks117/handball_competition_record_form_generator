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
from tkcalendar import DateEntry
from tkinter import ttk

def parse_date(date_str):
    try:
        # Convert input date string to datetime object
        return datetime.strptime(date_str, '%d/%m/%Y')
    except ValueError:
        raise ValueError("Invalid date format. Please use DD/MM/YYYY")

def run_application(match_type, target_date, referees):
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Download and read PDF
    if match_type == "聯賽":
        url = "https://www.handball.org.hk/2_Competition/2024-2025/聯賽/(92) 2024_LAEGUE_TIMETABLE_2025.03.18.pdf"
    elif match_type == "手總盃":
        url = "http://www.handball.org.hk/2_Competition/2024-2025/%E6%89%8B%E7%B8%BD%E7%9B%83/(4)%202024_%E6%89%8B%E7%B8%BD%E7%9B%83%E8%B3%BD%E7%A8%8B_2025.03.20.pdf"
    elif match_type == "港九學界":
        url = ""
    elif match_type == "屯門學界":
        url = "https://www.hkssf-nt.org.hk/district/sec/2024-2025/4.Tuen%20Mun/Handball/2425_TM_Junior_HB_Fixtures.pdf"

    url_ref = "http://www.handball.org.hk/6_Referee/2024-2025/2024-2025%E8%A3%81%E5%88%A4%E5%90%8D%E5%96%AE_20250226.pdf"
    
    content = download_and_read_pdf(url, match_type)
    ref_content = download_and_read_pdf(url_ref, "ref")

    if not content:
        raise Exception("Failed to read match PDF content")
    else:
        print("Match PDF content read successfully")
        update_txt_file(content, 'data.txt') 
        
    if not ref_content:
        raise Exception("Failed to read referee PDF content")
    else:
        print("Referee PDF content read successfully")
        update_txt_file(ref_content, 'ref_output.txt')

    # Extract and display matches
    matches = extract_matches_for_date(content, match_type, target_date)
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
    #template_path = "/Users/tszhowong/Desktop/Handball/Referee/Application/data/聯賽比賽記錄表_template.docx"
    template_path = "/Users/johnson/Desktop/Johnson/handball_competition_record_form_generator-main/data/聯賽比賽記錄表_template.docx"
    #template_path = filedialog.askopenfilename(title="Select Template File", filetypes=[("Word files", "*.docx")])

    if not template_path:
        raise Exception("No template file selected")
    else:
        # Create the new .docx file
        create_docx_from_template(template_path, match_type, matches, refs)
        messagebox.showinfo("Success", "Document generated successfully!")

def start_application():
    match_type = match_combobox.get()
    target_date = date_entry.get()
    referees = referee_entry.get().split(',')

    if not match_type:
        messagebox.showerror("Error", "Please select a match type")
        return

    try:
        parsed_date = parse_date(target_date)
        run_application(match_type, parsed_date, referees)  
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Setting up the UI with Tkinter
root = tk.Tk()
root.title("手球賽裁判記錄表生成器")
# Set window size to 400x400 pixels and position it at (100, 100)
root.geometry("400x400+100+100")

# Input for date using a dropdown list
tk.Label(root, text="Match Type:").pack(pady=5)
match_combobox = ttk.Combobox(root)
match_combobox['values'] = ['聯賽', '手總盃', '港九學界', '屯門學界']  # Replace with actual match type
match_combobox.pack(pady=5)

# Input for date using DateEntry from tkcalendar
tk.Label(root, text="Match Date:").pack(pady=5)
date_entry = DateEntry(root, date_pattern='dd/mm/yyyy')  # Set the date format
date_entry.pack(pady=5)

# Input for referees
tk.Label(root, text="Referee Numbers (comma-separated):").pack(pady=7)
referee_entry = tk.Entry(root)
referee_entry.pack(pady=5)

# Generate button
generate_button = tk.Button(root, text="Generate Document", command=start_application)
generate_button.pack(pady=20)

# Text area to display matches
# matches_output = tk.Text(root, height=10, width=50)
# matches_output.pack(pady=10)

# Run the application
root.mainloop()