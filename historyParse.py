#!/usr/bin/env python3
import sqlite3
import sys
import os
from datetime import datetime, timezone

EPOCH_DIFF = 11644473600  # seconds between 1601-01-01 and 1970-01-01
NO_TARGET_PATH = "<no target_path available>"

def get_file_size(total_bytes, received_bytes):
    """Get file size, preferring total_bytes, falling back to received_bytes, else 0."""
    if total_bytes is None:
        return received_bytes if received_bytes is not None else 0
    return total_bytes

def webkit_time_to_datetime(webkit_time):
    try:
        unix_ts = (webkit_time / 1_000_000.0) - EPOCH_DIFF
        return datetime.fromtimestamp(unix_ts, timezone.utc)
    except Exception:
        return None

def safe_fetch_count(cursor, query):
    try:
        cursor.execute(query)
        r = cursor.fetchone()
        return r[0] if r and r[0] is not None else 0
    except sqlite3.Error:
        return 0

def main():
    if len(sys.argv) < 2:
        print("Error! - No History File Specified!")
        sys.exit(1)

    history_file = sys.argv[1]

    if not os.path.exists(history_file):
        print("Error! - File Not Found!")
        sys.exit(1)

    db = None
    try:
        db = sqlite3.connect(f"file:{history_file}?mode=ro", uri=True)
        c = db.cursor()

        # 1) Source file
        print(f"Source File: {history_file}")

        # 2) Total number of downloads
        total_downloads = safe_fetch_count(c, "SELECT COUNT(*) FROM downloads")
        print(f"Total Downloads: {total_downloads}")

        # 3 & 4) List all downloaded files and their sizes
        print("Downloaded Files:")
        try:
            c.execute("""
                SELECT target_path, total_bytes, received_bytes
                FROM downloads
            """)
            rows = c.fetchall()
        except sqlite3.Error:
            rows = []

        if rows:
            idx = 1
            for row in rows:
                target_path, total_bytes, received_bytes = row
                file_size = get_file_size(total_bytes, received_bytes)
                if not target_path:
                    target_path = NO_TARGET_PATH
                # print each downloaded file and its size
                print(f" {idx}. File Name: {target_path}")
                print(f"    File Size: {file_size}")
                idx += 1
        else:
            print(" <no downloads found or downloads table missing>")

        # Find file that took the longest time to download
        try:
            c.execute("""
                SELECT target_path, total_bytes, received_bytes, (end_time - start_time) as duration
                FROM downloads
                WHERE end_time IS NOT NULL AND start_time IS NOT NULL
                ORDER BY duration DESC
                LIMIT 1
            """)
            longest_download = c.fetchone()
        except sqlite3.Error:
            longest_download = None

        if longest_download:
            target_path, total_bytes, received_bytes, duration = longest_download
            file_size = get_file_size(total_bytes, received_bytes)
            if not target_path:
                target_path = NO_TARGET_PATH
            print(f"Longest Download File Name: {target_path}")
            print(f"Longest Download File Size (bytes): {file_size}")
        else:
            print("Longest Download File Name: <none found>")
            print("Longest Download File Size (bytes): <n/a>")

        # 5) Number of unique search terms
        unique_search_terms = safe_fetch_count(c, "SELECT COUNT(DISTINCT term) FROM keyword_search_terms")
        print(f"Unique Search Terms: {unique_search_terms}")

        # 6 & 7) Most recent search term and its date/time
        try:
            c.execute("""
                SELECT kst.term, u.last_visit_time
                FROM keyword_search_terms kst
                INNER JOIN urls u ON kst.url_id = u.id
                WHERE u.last_visit_time IS NOT NULL
                ORDER BY u.last_visit_time DESC
                LIMIT 1
            """)
            recent = c.fetchone()
        except sqlite3.Error:
            recent = None

        if recent and recent[0] is not None:
            term, webkit_time = recent
            dt = webkit_time_to_datetime(webkit_time) if webkit_time is not None else None
            formatted = dt.strftime("%Y-%b-%d %H:%M:%S") if dt else "<invalid date>"
            print(f"Most Recent Search: {term}")
            print(f"Most Recent Search Date/Time: {formatted}")
        else:
            print("Most Recent Search: <none found>")
            print("Most Recent Search Date/Time: <n/a>")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main()