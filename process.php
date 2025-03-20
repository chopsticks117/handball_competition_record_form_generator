<?php
// Set appropriate headers for JSON response
header('Content-Type: application/json');

// Check if date is provided
if (!isset($_POST['date'])) {
    echo json_encode(['error' => 'Date is required']);
    exit;
}

// Get the date from POST request
$date = $_POST['date'];

// Validate date format (DD/MM/YYYY)
if (!preg_match('/^\d{2}\/\d{2}\/\d{4}$/', $date)) {
    echo json_encode(['error' => 'Invalid date format. Please use DD/MM/YYYY']);
    exit;
}

// Create data directory if it doesn't exist
$dataDir = 'data';
if (!file_exists($dataDir)) {
    mkdir($dataDir, 0755, true);
}

// Define the PDF URL
$pdfUrl = "https://www.handball.org.hk/2_Competition/2024-2025/聯賽/(92) 2024_LAEGUE_TIMETABLE_2025.03.18.pdf";

// Define the path to store the PDF content
$pdfContentFile = "$dataDir/pdf_content.txt";
$matchesFile = "$dataDir/matches_$date.json";

// Function to download and process PDF
function downloadAndProcessPdf($url, $contentFile) {
    // Check if we already have the PDF content cached
    if (file_exists($contentFile) && (time() - filemtime($contentFile) < 86400)) { // 24 hours cache
        return file_get_contents($contentFile);
    }
    
    // Require the PDF parser library
    // Note: You'll need to install this via Composer
    // composer require smalot/pdfparser
    require_once 'vendor/autoload.php';
    
    try {
        // Initialize a cURL session
        $ch = curl_init();
        
        // Set cURL options
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
        
        // Execute cURL session and get the content
        $pdfContent = curl_exec($ch);
        
        // Check for cURL errors
        if (curl_errno($ch)) {
            throw new Exception('cURL error: ' . curl_error($ch));
        }
        
        // Close cURL session
        curl_close($ch);
        
        // Parse PDF content
        $parser = new \Smalot\PdfParser\Parser();
        $pdf = $parser->parseContent($pdfContent);
        
        // Extract text from all pages
        $text = '';
        foreach ($pdf->getPages() as $page) {
            $text .= $page->getText();
        }
        
        // Save the extracted text to file
        file_put_contents($contentFile, $text);
        
        return $text;
    } catch (Exception $e) {
        return false;
    }
}

// Function to extract matches for a specific date
function extractMatchesForDate($content, $targetDate) {
    // Parse the target date
    list($day, $month, $year) = explode('/', $targetDate);
    $day = (int)$day;
    $month = (int)$month;
    $year = (int)$year;
    
    $matches = [];
    
    // Split content into lines
    $lines = explode("\n", $content);
    
    // Find all year markers first
    $yearIndices = [];
    $foundYearIndex = 0;
    foreach ($lines as $i => $line) {
        if (preg_match('/(\d{4})年/', $line, $yearMatch) && (int)$yearMatch[1] === $year) {
            $yearIndices[] = $i;
        }
    }
    
    // For each year marker, look for the target month and day
    $dateBlockFound = false;
    $dateBlockIndex = -1;
    $venue = "Unknown";
    $foundIndicator = "";
    
    foreach ($yearIndices as $yearIdx) {
        for ($i = $yearIdx; $i < min($yearIdx + 10, count($lines)); $i++) {
            if (preg_match('/(\d+)月/', $lines[$i], $monthMatch) && (int)$monthMatch[1] === $month) {
                // Found the month, now look for the day
                $dayMatch = preg_match('/月' . $day . '日/', $lines[$i]) || 
                            preg_match('/月' . $day . '\s/', $lines[$i]) || 
                            preg_match('/月' . $day . '$/', $lines[$i]);
                
                if ($dayMatch) {
                    $dateBlockFound = true;
                    $dateBlockIndex = $i;
                } elseif ($i + 1 < count($lines) && (
                    preg_match('/^' . $day . '日/', $lines[$i + 1]) || 
                    preg_match('/^' . $day . '\s/', $lines[$i + 1]) || 
                    preg_match('/^' . $day . '$/', $lines[$i + 1])
                )) {
                    $dateBlockFound = true;
                    $dateBlockIndex = $i;
                }
                
                if ($dateBlockFound) {
                    // Extract venue from the same or next lines
                    $venueFound = false;
                    $lineIndex = $dateBlockIndex;  // Start looking from the date block line
                    $venueLines = [];  // To accumulate lines for the venue

                    while ($lineIndex < count($lines)) {
                        $line = trim($lines[$lineIndex]);

                        // Check for the day suffix first
                        if (strpos($line, '日(') !== false) {
                            // Extract the venue part after the day suffix
                            if (preg_match('/日\([日一二三四五六]\)/', $line, $daySuffixMatch)) {
                                $venuePart = trim(substr($line, strlen($daySuffixMatch[0])));
                                $venueLines[] = $venuePart;  // Add to venue lines
                            }
                        } elseif (preg_match('/^\([日一二三四五六]\)/', $line, $daySuffixMatch)) {
                            $venuePart = trim(substr($line, strlen($daySuffixMatch[0])));
                            $venueLines[] = $venuePart;  // Add to venue lines
                        }
                            
                        // If we find a venue indicator in the current line, extract it
                        $venueIndicators = ["場", "心", "館", "園"];
                        foreach ($venueIndicators as $indicator) {
                            if (strpos($line, $indicator) !== false) {
                                $venueLines[] = $line;  // Add the whole line if it contains the indicator
                                $foundIndicator = $indicator;
                                $venueFound = true;
                                break;
                            }
                        }
        
                        // Stop if we find a line that indicates a match entry or is not relevant
                        if (preg_match('/^\d+\s+/', $line) || strpos($line, '成 績') !== false) {
                            break;
                        }

                        $lineIndex++;
                    }

                    // Join all collected venue lines and clean up
                    if (!empty($venueLines)) {
                        $venue = str_replace(" ", "", implode('', $venueLines));  // Remove spaces between parts
                        $venueParts = explode($foundIndicator, $venue);
                        $venue = $venueParts[0] . $foundIndicator; // Clean up any numbers
                        $venueFound = true;
                    }
                }
            }
            
            if ($dateBlockFound) {
                $foundYearIndex = $yearIdx;
                break;
            }
        }
        
        if ($dateBlockFound) {
            break;
        }
    }
    
    if ($dateBlockFound) {
        // Start processing matches
        $startIdx = $dateBlockIndex + 1;
        
        // Process match entries
        while ($startIdx < count($lines)) {
            $line = trim($lines[$startIdx]);
            
            // Check if this is a match entry (starts with a number)
            if (preg_match('/^\d+\s+/', $line)) {
                // Check if this is a match entry with time
                preg_match('/(\d{4}-\d{4})/', $line, $timeMatch);
                
                preg_match('/^(\d+)/', $line, $matchNumMatch);
                $matchNum = $matchNumMatch[1];
                
                // If there's a time, extract it
                $timeRange = "";
                if (!empty($timeMatch)) {
                    $timeRange = $timeMatch[1];
                }
                
                // Extract team and group information
                if (preg_match('/(男|女)([甲乙丙])\s*(\d+)組\s+(\S+)\s+(\S+)/', $line, $teamMatch)) {
                    $gender = $teamMatch[1];
                    $level = $teamMatch[2];
                    $groupNum = $teamMatch[3];
                    $homeTeam = trim($teamMatch[4]);
                    $awayTeam = trim($teamMatch[5]);
                    
                    $group = $gender . $level . $groupNum . '組';
                    
                    $matches[] = [
                        '場次' => $matchNum,
                        '日期' => "$day/$month/$year",
                        '地點' => $venue,
                        '時間' => $timeRange,
                        '組別' => $group,
                        '主隊' => $homeTeam,
                        '客隊' => $awayTeam
                    ];
                }
            }
            
            // Check for a special case where matches are listed right after the venue line
            elseif (strpos($line, $foundIndicator) === 0) {
                // Extract match number and details
                preg_match('/^\d+/', $lines[$foundYearIndex], $matchNumMatch);
                $matchNum = $matchNumMatch[0];
                
                if (preg_match('/(\S+)\s+(\S+)/', $line, $homeAwayMatch)) {
                    $homeTeam = trim($homeAwayMatch[1]);
                    $awayTeam = trim($homeAwayMatch[2]);
                    $matches[] = [
                        '場次' => $matchNum,
                        '日期' => "$day/$month/$year",
                        '地點' => $venue,
                        '時間' => $timeRange ?? '',
                        '組別' => 'Unknown',  // You might want to refine this
                        '主隊' => $homeTeam,
                        '客隊' => $awayTeam
                    ];
                }
            }
                
            // If we find another year marker or end of relevant data, break
            if (preg_match('/\d+年/', $line)) {
                break;
            }
            
            $startIdx++;
        }
    }
    
    return $matches;
}

// Main processing logic
try {
    // Check if we already have the matches for this date
    if (file_exists($matchesFile) && (time() - filemtime($matchesFile) < 86400)) { // 24 hours cache
        $matches = json_decode(file_get_contents($matchesFile), true);
    } else {
        // Download and process the PDF
        $pdfContent = downloadAndProcessPdf($pdfUrl, $pdfContentFile);
        
        if (!$pdfContent) {
            echo json_encode(['error' => 'Failed to download or process the PDF']);
            exit;
        }
        
        // Extract matches for the specified date
        $matches = extractMatchesForDate($pdfContent, $date);
        
        // Save matches to file for caching
        file_put_contents($matchesFile, json_encode($matches));
    }
    
    // Return the matches as JSON
    echo json_encode(['matches' => $matches]);
    
} catch (Exception $e) {
    echo json_encode(['error' => 'An error occurred: ' . $e->getMessage()]);
}
?>
