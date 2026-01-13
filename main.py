import os
import sys
import re
from db_manager import DBManager
from analyzer import Analyzer

def parse_history_line(line: str):
    """
    Parse a line from .bash_history.
    Handle timestamps (lines starting with #).
    Ignore lines starting with space.
    Return (full_command, base_cmd, params) or None.
    """
    line = line.rstrip('\n')
    
    if not line:
        return None
        
    # Ignore timestamps for now (they are on separate lines usually in bash history)
    # Typically bash history with timestamps looks like:
    # #1678888888
    # command
    # So if we see a line starting with # and all digits, it's a timestamp.
    # The prompt says: "Handle lines with and without timestamps."
    # If it's a timestamp line, we probably just skip it as it's not a command.
    if line.startswith('#') and line[1:].isdigit():
        return None
        
    # Ignore lines starting with a space
    if line.startswith(' '):
        return None
        
    full_command = line.strip()
    if not full_command:
        return None
        
    parts = full_command.split(maxsplit=1)
    base_cmd = parts[0]
    params = parts[1] if len(parts) > 1 else ""
    
    return full_command, base_cmd, params

def process_history_file(file_path: str, db: DBManager):
    """Read history file and populate DB."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    print(f"Reading from {file_path}...")
    try:
        # Bash history can have some encoding issues, usually it's utf-8 or latin-1
        with open(file_path, 'r', errors='replace') as f:
            for line in f:
                result = parse_history_line(line)
                if result:
                    full_cmd, base_cmd, params = result
                    db.insert_command(full_cmd, base_cmd, params)
    except Exception as e:
        print(f"Error reading file: {e}")

def main():
    db_path = "bash_history.db"
    history_path = os.path.expanduser("~/.bash_history")
    
    # Allow overriding path via env var or arg for testing
    if len(sys.argv) > 1:
        history_path = sys.argv[1]
    
    # Initialize DB
    db = DBManager(db_path)
    db.init_db()
    
    # Process History
    process_history_file(history_path, db)
    
    # Analyze
    analyzer = Analyzer(db)
    
    print("\n--- Bash History Analysis ---\n")
    
    # 1. Top 50 Commands
    print("1. Top 50 Most Frequent Commands:")
    top_50 = analyzer.get_top_50_commands()
    for i, (cmd, freq) in enumerate(top_50, 1):
        print(f"{i:>2}. {cmd} ({freq})")
    print()
    
    # 2. Typo Detection
    print("2. Potential Typos (freq < 3, similar to high-freq commands):")
    typos = analyzer.detect_typos()
    if not typos:
        print("No typos detected.")
    else:
        for typo, likely, freq in typos:
            print(f"  '{typo}' (freq: {freq}) -> Did you mean '{likely}'?")
    print()
    
    # 3. Alias Suggestions
    print("3. Alias Suggestions (freq > 10, len > 15):")
    aliases = analyzer.suggest_aliases()
    if not aliases:
        print("No alias suggestions found.")
    else:
        for cmd, freq in aliases:
            print(f"  Consider aliasing: '{cmd}' (used {freq} times)")
    print()

if __name__ == "__main__":
    main()
