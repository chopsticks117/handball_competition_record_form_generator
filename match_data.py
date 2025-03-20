from tabulate import tabulate
import re

debug = False

def extract_matches_for_date(content, target_date):
    matches = []
    
    # Format the target date for comparison
    target_day = target_date.day
    target_month = target_date.month
    target_year = target_date.year
    
    # Split content into lines
    lines = content.split('\n')
    
    if debug:
        print(f"Looking for matches on {target_day}/{target_month}/{target_year}")
    
    # Find all year markers first
    year_indices = []
    for i, line in enumerate(lines):
        year_match = re.search(r'(\d{4})年', line)
        if year_match and int(year_match.group(1)) == target_year:
            year_indices.append(i)
    
    # For each year marker, look for the target month and day
    date_block_found = False
    date_block_index = -1
    venue = "Unknown"
    found_indicator = ""
    
    for year_idx in year_indices:
        for i in range(year_idx, min(year_idx + 10, len(lines))):
            month_match = re.search(r'(\d+)月', lines[i])
            
            if month_match and int(month_match.group(1)) == target_month:
                # Found the month, now look for the day
                day_match = re.search(f'月{target_day}日', lines[i]) or re.search(f'月{target_day}\\s', lines[i]) or re.search(f'月{target_day}$', lines[i])
                
                if day_match:
                    date_block_found = True
                    date_block_index = i
                elif i + 1 < len(lines) and (
                    re.search(f'^{target_day}日', lines[i + 1]) or 
                    re.search(f'^{target_day}\\s', lines[i + 1]) or
                    re.search(f'^{target_day}$', lines[i + 1])
                ):
                    date_block_found = True
                    date_block_index = i
                
                
                if date_block_found:
                    # Extract venue from the same or next lines
                    venue_found = False
                    line_index = date_block_index  # Start looking from the date block line

                    # Continue searching for the venue until we find it or reach a limit
                    venue_lines = []  # To accumulate lines for the venue

                    while line_index < len(lines):
                        line = lines[line_index].strip()

                        # Check for the day suffix first
                        if ')' in line:
                            # Extract the venue part after the day suffix
                            day_suffix_match_1 = re.search(r'日\([日一二三四五六]\)', line)
                            day_suffix_match_2 = re.search(r'^\([日一二三四五六]\)', line)

                            if day_suffix_match_1:
                                venue_part = line[day_suffix_match_1.end():].strip()
                                venue_lines.append(venue_part)  # Add to venue lines
                            elif day_suffix_match_2:
                                venue_part = line[day_suffix_match_2.end():].strip()
                                venue_lines.append(venue_part)  # Add to venue lines
                        elif False: #re.search(r'^\s*', line):
                            space_suffix_match = re.search(r'^\s*', line)
                            if space_suffix_match:
                                venue_part = line[space_suffix_match.end():].strip()
                                venue_lines.append(venue_part)  # Add to venue lines
                            
                        # If we find a venue indicator in the current line, extract it
                        venue_indicators = ["場", "心", "館", "園"]
                        for indicator in venue_indicators:
                            if indicator in line:
                                venue_lines.append(line)  # Add the whole line if it contains the indicator
                                found_indicator = indicator
                                venue_found = True
                                break
        
                        # Stop if we find a line that indicates a match entry or is not relevant
                        if re.match(r'^\d+\s+', line) or '成 績' in line:
                            break

                        line_index += 1

                    # Join all collected venue lines and clean up
                    if venue_lines:
                        venue = ''.join(venue_lines).replace(" ", "").strip()  # Remove spaces between parts
                        before_indicator = venue.split(found_indicator)[0].strip()
                        venue = before_indicator + found_indicator # Clean up any numbers
                        venue_found = True

                    if not venue_found:
                        print("Venue not found.")
            
            if date_block_found:
                break
        
        if date_block_found:
            break
    
    if date_block_found:
        if debug:
            print(f"Found date block at line {date_block_index}: {lines[date_block_index]}")
            if date_block_index + 1 < len(lines):
                print(f"Next line: {lines[date_block_index + 1]}")
            print(f"Venue: {venue}")
        
        # Start processing matches
        start_idx = date_block_index + 1
        
        # Process match entries
        while start_idx < len(lines):
            line = lines[start_idx].strip()
            
            match_num = 0
            
            # Check if this is a match entry (starts with a number)
            if re.match(r'^\d+\s+', line):
                match_num = re.match(r'^(\d+)', line).group(1)
            elif re.match(r'^(\d+)', lines[date_block_index-2]):
                match_num = re.match(r'^(\d+)', lines[date_block_index-2]).group(1)
            else:
                match_num = re.match(r'^(\d+)', lines[date_block_index-1]).group(0)
            
            # Check if this is a match entry with time
            time_match = re.search(r'(\d{4}-\d{4})', line)
                
                 
            # If there's a time, extract it
            time_range = ""
            if time_match:
                time_range = time_match.group(1)
            else:
                time_range = "比賽改期"
                
            # Extract team and group information
            team_match = re.search(r'(男|女)([甲乙丙])\s*(\d+)組\s+(\S+)\s+(\S+)', line)
            if not team_match: #手總盃
                team_match = re.search(r'(男|女)([盾碟盃])\s*(\S+)組\s+(\S+)\s+(\S+)', line)
                
            if team_match:
                gender = team_match.group(1)
                level = team_match.group(2)
                group_num = team_match.group(3)
                home_team = team_match.group(4).strip()
                away_team = team_match.group(5).strip()
                    
                group = f"{gender}{level} {group_num} 組"
                    
                matches.append({
                    '場次': match_num,
                    '日期': f"{target_day}/{target_month}/{target_year}",
                    '地點': venue,
                    '時間': time_range,
                    '組別': group,
                    '主隊': home_team,
                    '客隊': away_team
                })
            
                
            # If we find another year marker or end of relevant data, break
            if re.search(r'\d+年', line):
                break
            
            start_idx += 1
    
    return matches

def display_matches(matches):
    if not matches:
        print("No matches found for the specified date.")
        return
    
    # Prepare data for tabulate
    headers = ['場次', '日期', '地點', '時間', '組別', '主隊', '客隊']
    
    # Format the data for better alignment
    formatted_data = []
    for match in matches:
        formatted_row = [
            match['場次'],
            match['日期'],
            match['地點'],
            match['時間'],
            match['組別'],
            match['主隊'],
            match['客隊']
        ]
        formatted_data.append(formatted_row)
    
    # Print table with better formatting
    print(tabulate(formatted_data, headers=headers, tablefmt='pretty', colalign=('center', 'center', 'left', 'center', 'center', 'center', 'center')))
