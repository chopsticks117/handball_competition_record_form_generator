from tabulate import tabulate

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j]['裁判編號'] > arr[j + 1]['裁判編號']:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def extract_referees(content, referees):
    referees_info = []
    lines = content.split('\n')
    for line in lines:
        line = line.split()
        for ref_num in referees:
            ref_name = ""
            for i in range(0, len(line), 2):
                if i+1 < len(line) and line[i] == ref_num:
                    ref_name = line[i+1]
            if ref_num in line:
                referees_info.append({
                    '裁判編號': ref_num,
                    '裁判姓名': ref_name
                })
    return bubble_sort(referees_info)

def display_referee(refs):
    if not refs:
        print("No referees found for the specified number.")
        return
    
    # Prepare data for tabulate
    headers = ['裁判編號', '裁判姓名']
    
    # Format the data for better alignment
    formatted_data = []
    for ref in refs:
        formatted_row = [
            ref['裁判編號'],
            ref['裁判姓名'],
        ]
        formatted_data.append(formatted_row)
    
    # Print table with better formatting
    print(tabulate(formatted_data, headers=headers, tablefmt='pretty', colalign=('center', 'center')))
