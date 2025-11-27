import sqlite3
import sys
import os
import ntpath
from datetime import datetime, timezone

# check if user gave us a file
if len(sys.argv) < 2:
    print("Error! - No History File Specified!")
    sys.exit(1)

# get the file name
file = sys.argv[1]

# check if file exist
if not os.path.exists(file):
    print("Error! - File Not Found!")
    sys.exit(1)

try:
    # open database
    db = sqlite3.connect(file)
    c = db.cursor()
    
    # print file name
    print(f"Source File: {file}")
    print()
    
    # count all downloads
    c.execute("SELECT COUNT(*) FROM downloads")
    result = c.fetchone()
    num = result[0]
    print(f"Total Downloads: {num}")
    print()
    
    # find longest download by calculating actual duration
    # Chrome stores times in microseconds since Windows epoch (1601)
    c.execute("""
        SELECT target_path, total_bytes, 
               (end_time - start_time) as download_duration
        FROM downloads
        WHERE end_time IS NOT NULL 
        AND start_time IS NOT NULL
        AND (end_time - start_time) > 0
        ORDER BY download_duration DESC
        LIMIT 1
    """)
    result = c.fetchone()
    
    if result:
        path = result[0]
        size = result[1]
        
        # handle if size is None
        if size is None:
            size = 0
        
        # Extract filename using ntpath to handle Windows-style paths on any OS
        name = ntpath.basename(path)
        
        print(f"Longest Download: {name}")
        print(f"Longest Download Bytes: {size}")
        print()
    
    # count unique search term
    c.execute("SELECT COUNT(DISTINCT term) FROM keyword_search_terms")
    result = c.fetchone()
    searches = result[0]
    print(f"Unique Search Terms: {searches}")
    print()
    
    # get most recent search term using proper join
    c.execute("""
        SELECT kst.term, u.last_visit_time
        FROM keyword_search_terms kst
        INNER JOIN urls u ON kst.url_id = u.id
        WHERE u.last_visit_time IS NOT NULL
        ORDER BY u.last_visit_time DESC
        LIMIT 1
    """)
    result = c.fetchone()
    
    if result:
        term = result[0]
        webkit_time = result[1]
        
        # Convert Chrome WebKit timestamp to Python datetime
        # WebKit epoch: January 1, 1601 (Windows FILETIME epoch)
        # Unix epoch: January 1, 1970
        # Difference: 11644473600 seconds
        EPOCH_DIFF = 11644473600
        
        # Convert microseconds to seconds and adjust for epoch
        unix_timestamp = (webkit_time / 1000000.0) - EPOCH_DIFF
        
        # Convert to datetime using timezone-aware method
        dt = datetime.fromtimestamp(unix_timestamp, timezone.utc)
        
        # Format the date
        date = dt.strftime("%m/%d/%Y %H:%M:%S")
        
        print(f"Most Recent Search Term: {term}")
        print(f"Most Recent Search Date/Time: {date}")
    
    # close database
    db.close()
    
except sqlite3.Error as e:
    print("Error! - File Not Found!")
    sys.exit(1)
except Exception as e:
    print("Error! - File Not Found!")
    sys.exit(1)