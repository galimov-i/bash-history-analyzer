import sqlite3
from typing import List, Tuple, Dict

class DBManager:
    def __init__(self, db_name="bash_history.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def init_db(self):
        self.connect()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_command TEXT,
                base_cmd TEXT,
                params TEXT,
                UNIQUE(full_command)
            )
        ''')
        # We also need a way to track frequency, either by inserting every occurrence or by having a count.
        # The requirements say "Insert parsed commands... Columns: id, full_command, base_cmd, params".
        # If we insert every occurrence, we can count them later.
        # But `UNIQUE(full_command)` would prevent duplicates.
        # If the requirement implies storing every historical entry, we should remove UNIQUE and store all.
        # "Parse: Read ~/.bash_history... Store: Insert parsed commands" suggests storing the history.
        # A typical history file has duplicates. Storing every entry allows temporal analysis if we had timestamps,
        # but here we just need frequency.
        # However, the requirement says "Columns: id, full_command, base_cmd, params".
        # If I strictly follow the columns, I can't add a 'count' column easily without deviating or aggregating on insert.
        # But to analyze frequency, I must either store all occurrences (no UNIQUE) or store count.
        # Storing all occurrences is safer for "Store: Insert parsed commands".
        # Let's drop the UNIQUE constraint to allow storing command history as a log.
        
        self.cursor.execute('DROP TABLE IF EXISTS commands') # Re-create to ensure schema
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_command TEXT,
                base_cmd TEXT,
                params TEXT
            )
        ''')
        self.conn.commit()
        self.close()

    def insert_command(self, full_command: str, base_cmd: str, params: str):
        self.connect()
        self.cursor.execute('''
            INSERT INTO commands (full_command, base_cmd, params)
            VALUES (?, ?, ?)
        ''', (full_command, base_cmd, params))
        self.conn.commit()
        self.close()

    def get_command_frequencies(self) -> List[Tuple[str, int]]:
        self.connect()
        self.cursor.execute('''
            SELECT full_command, COUNT(*) as freq
            FROM commands
            GROUP BY full_command
            ORDER BY freq DESC
        ''')
        results = self.cursor.fetchall()
        self.close()
        return results

    def get_base_cmd_frequencies(self) -> List[Tuple[str, int]]:
        self.connect()
        self.cursor.execute('''
            SELECT base_cmd, COUNT(*) as freq
            FROM commands
            GROUP BY base_cmd
            ORDER BY freq DESC
        ''')
        results = self.cursor.fetchall()
        self.close()
        return results
