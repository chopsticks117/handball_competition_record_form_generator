// We need to use a PDF.js library for parsing PDFs in the browser
// First, let's include the PDF.js library in your HTML file
// Add this to your HTML head section:
// <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.min.js"></script>

document.addEventListener('DOMContentLoaded', function() {
    // Initialize PDF.js worker
    if (typeof pdfjsLib !== 'undefined') {
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
    }

    document.getElementById('matchForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const dateInput = document.getElementById('date').value;
        if (!dateInput) {
            alert("Please select a date");
            return;
        }
        
        // Convert from YYYY-MM-DD to DD/MM/YYYY format
        const dateParts = dateInput.split('-');
        if (dateParts.length !== 3) {
            alert("Invalid date format");
            return;
        }
        
        const formattedDate = `${dateParts[2]}/${dateParts[1]}/${dateParts[0]}`;
        const targetDate = parseDate(formattedDate);
        
        if (!targetDate) {
            alert("Invalid date format. Please use DD/MM/YYYY");
            return;
        }
        
        // Show loading spinner
        document.getElementById('loading').style.display = 'block';
        document.getElementById('results').innerHTML = '';
        
        try {
            const pdfUrl = "http://www.handball.org.hk/2_Competition/2024-2025/聯賽/(92) 2024_LAEGUE_TIMETABLE_2025.03.18.pdf";
            const content = await downloadAndReadPdf(pdfUrl);
            
            if (!content) {
                throw new Error("Failed to read PDF content");
            }
            
            const matches = extractMatchesForDate(content, targetDate);
            displayMatches(matches);
        } catch (error) {
            document.getElementById('results').innerHTML = `
                <div class="error-message">
                    Error: ${error.message}
                </div>
            `;
            console.error(error);
        } finally {
            // Hide loading spinner
            document.getElementById('loading').style.display = 'none';
        }
    });
});

function parseDate(dateStr) {
    const parts = dateStr.split('/');
    if (parts.length !== 3) return null;

    const day = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10);
    const year = parseInt(parts[2], 10);
    
    const date = new Date(year, month - 1, day); // month is 0-indexed
    
    // Validate the date
    if (isNaN(date.getTime())) return null;
    
    return date;
}

async function downloadAndReadPdf(url) {
    try {
        // Fetch the PDF
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const arrayBuffer = await response.arrayBuffer();
        
        // Load the PDF using PDF.js
        const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        let content = "";
        
        // Extract text from all pages
        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const textContent = await page.getTextContent();
            content += textContent.items.map(item => item.str).join(' ');
        }
        
        return content;
    } catch (error) {
        console.error("Error downloading or reading PDF:", error);
        throw error;
    }
}

function extractMatchesForDate(content, targetDate) {
    const matches = [];
    
    // Format the target date for comparison
    const targetDay = targetDate.getDate();
    const targetMonth = targetDate.getMonth() + 1; // Months are 0-indexed in JavaScript
    const targetYear = targetDate.getFullYear();
    
    // Split content into lines
    const lines = content.split('\n');
    
    console.log(`Looking for matches on ${targetDay}/${targetMonth}/${targetYear}`);
    
    // Find all year markers first
    const yearIndices = [];
    for (let i = 0; i < lines.length; i++) {
        const yearMatch = lines[i].match(/(\d{4})年/);
        if (yearMatch && parseInt(yearMatch[1]) === targetYear) {
            yearIndices.push(i);
        }
    }
    
    // For each year marker, look for the target month and day
    let dateBlockFound = false;
    let dateBlockIndex = -1;
    let venue = "Unknown";
    let foundIndicator = "";
    
    for (const yearIdx of yearIndices) {
        for (let i = yearIdx; i < Math.min(yearIdx + 10, lines.length); i++) {
            const monthMatch = lines[i].match(/(\d+)月/);
            
            if (monthMatch && parseInt(monthMatch[1]) === targetMonth) {
                // Found the month, now look for the day
                const dayMatch = lines[i].match(`月${targetDay}日`) || lines[i].match(`月${targetDay}\\s`) || lines[i].match(`月${targetDay}$`);
                
                if (dayMatch) {
                    dateBlockFound = true;
                    dateBlockIndex = i;
                } else if (i + 1 < lines.length && (
                    lines[i + 1].match(`^${targetDay}日`) || 
                    lines[i + 1].match(`^${targetDay}\\s`) ||
                    lines[i + 1].match(`^${targetDay}$`)
                )) {
                    dateBlockFound = true;
                    dateBlockIndex = i;
                }
                
                if (dateBlockFound) {
                    // Extract venue from the same or next lines
                    let venueFound = false;
                    let lineIndex = dateBlockIndex;  // Start looking from the date block line

                    // Continue searching for the venue until we find it or reach a limit
                    const venueLines = [];  // To accumulate lines for the venue

                    while (lineIndex < lines.length) {
                        const line = lines[lineIndex].trim();

                        // Check for the day suffix first
                        if (line.includes('日(')) {
                            // Extract the venue part after the day suffix
                            const daySuffixMatch = line.match(/日\([日一二三四五六]\)/);
                            if (daySuffixMatch) {
                                const venuePart = line.slice(daySuffixMatch.index + daySuffixMatch[0].length).trim();
                                venueLines.push(venuePart);  // Add to venue lines
                            }
                        } else if (line.match(/^\([日一二三四五六]\)/)) {
                            const daySuffixMatch = line.match(/^\([日一二三四五六]\)/);
                            if (daySuffixMatch) {
                                const venuePart = line.slice(daySuffixMatch.index + daySuffixMatch[0].length).trim();
                                venueLines.push(venuePart);  // Add to venue lines
                            }
                        }
                        
                        // If we find a venue indicator in the current line, extract it
                        const venueIndicators = ["場", "心", "館", "園"];
                        for (const indicator of venueIndicators) {
                            if (line.includes(indicator)) {
                                venueLines.push(line);  // Add the whole line if it contains the indicator
                                foundIndicator = indicator;
                                venueFound = true;
                                break;
                            }
                        }

                        // Stop if we find a line that indicates a match entry or is not relevant
                        if (line.match(/^\d+\s+/) || line.includes('成 績')) {
                            break;
                        }

                        lineIndex++;
                    }

                    // Join all collected venue lines and clean up
                    if (venueLines.length > 0) {
                        venue = venueLines.join('').replace(/\s+/g, '').trim();  // Remove spaces between parts
                        const beforeIndicator = venue.split(foundIndicator)[0].trim();
                        venue = beforeIndicator + foundIndicator; // Clean up any numbers
                        venueFound = true;
                    }

                    if (!venueFound) {
                        console.log("Venue not found.");
                    }
                }
            }

            if (dateBlockFound) {
                break;
            }
        }

        if (dateBlockFound) {
            break;
        }
    }

    if (dateBlockFound) {
        console.log(`Found date block at line ${dateBlockIndex}: ${lines[dateBlockIndex]}`);
        if (dateBlockIndex + 1 < lines.length) {
            console.log(`Next line: ${lines[dateBlockIndex + 1]}`);
        }
        console.log(`Venue: ${venue}`);
        
        // Start processing matches
        let startIdx = dateBlockIndex + 1;
        
        // Process match entries
        while (startIdx < lines.length) {
            const line = lines[startIdx].trim();
            
            // Check if this is a match entry (starts with a number)
            const matchNumMatch = line.match(/^(\d+)\s+/);
            if (matchNumMatch) {
                const matchNum = matchNumMatch[1];
                
                // Check if this is a match entry with time
                const timeMatch = line.match(/(\d{4}-\d{4})/);
                const timeRange = timeMatch ? timeMatch[1] : "";
                
                // Extract team and group information
                const teamMatch = line.match(/(男|女)([甲乙丙])\s*(\d+)組\s+(\S+)\s+(\S+)/);
                
                if (teamMatch) {
                    const gender = teamMatch[1];
                    const level = teamMatch[2];
                    const groupNum = teamMatch[3];
                    const homeTeam = teamMatch[4].trim();
                    const awayTeam = teamMatch[5].trim();
                    
                    const group = `${gender}${level}${groupNum}組`;
                    
                    matches.push({
                        '場次': matchNum,
                        '日期': `${targetDay}/${targetMonth}/${targetYear}`,
                        '地點': venue,
                        '時間': timeRange,
                        '組別': group,
                        '主隊': homeTeam,
                        '客隊': awayTeam
                    });
                }
            }
            
            // Check for a special case where matches are listed right after the venue line
            else if (line.includes(foundIndicator)) {
                // Extract match number and details
                const matchNum = lines[dateBlockIndex].match(/^\d+/)[0];
                const homeAwayMatch = line.match(/(\S+)\s+(\S+)/);
                
                if (homeAwayMatch) {
                    const homeTeam = homeAwayMatch[1].trim();
                    const awayTeam = homeAwayMatch[2].trim();
                    matches.push({
                        '場次': matchNum,
                        '日期': `${targetDay}/${targetMonth}/${targetYear}`,
                        '地點': venue,
                        '時間': timeRange,
                        '組別': 'Unknown',  // You might want to refine this
                        '主隊': homeTeam,
                        '客隊': awayTeam
                    });
                }
            }
            
            // If we find another year marker or end of relevant data, break
            if (line.match(/\d+年/)) {
                break;
            }
            
            startIdx++;
        }
    }

    return matches;
}

function displayMatches(matches) {
    const resultsDiv = document.getElementById('results');
    if (!matches.length) {
        resultsDiv.innerHTML = '<div class="no-matches">No matches found for the specified date.</div>';
        return;
    }
    
    const table = document.createElement('table');
    table.classList.add('matches-table');
    
    // Create table headers
    const headers = ['場次', '日期', '地點', '時間', '組別', '主隊', '客隊'];
    const headerRow = document.createElement('tr');
    headers.forEach(headerText => {
        const header = document.createElement('th');
        header.textContent = headerText;
        headerRow.appendChild(header);
    });
    table.appendChild(headerRow);
    
    // Create table rows
    matches.forEach(match => {
        const row = document.createElement('tr');
        headers.forEach(header => {
            const cell = document.createElement('td');
            cell.textContent = match[header];
            row.appendChild(cell);
        });
        table.appendChild(row);
    });
    
    resultsDiv.innerHTML = '';
    resultsDiv.appendChild(table);
}