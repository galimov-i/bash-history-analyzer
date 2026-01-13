# Bash History Analyzer

A CLI tool built with Python and SQLite to analyze your bash history, identify frequent commands, detect potential typos, and suggest useful aliases.

## Features

- **Parse & Store**: Reads `~/.bash_history`, parsing commands and storing them in a local SQLite database for analysis.
- **Top Commands**: Identifies your Top-50 most frequently used commands.
- **Typo Detection**: Finds low-frequency commands that are very similar (Levenshtein distance < 2) to your high-frequency commands (e.g., `gti` vs `git`).
- **Alias Suggestions**: Suggests short aliases for long commands (> 15 chars) that you use frequently (> 10 times).

## Requirements

- Python 3.6+
- Standard Python libraries (`sqlite3`, `difflib`, `os`, `sys`, `re`)

## Installation

Clone the repository:

```bash
git clone https://github.com/galimov-i/bash-history-analyzer.git
cd bash-history-analyzer
```

## Usage

Run the analyzer with default settings (reads from `~/.bash_history`):

```bash
python3 main.py
```

Or specify a custom history file path:

```bash
python3 main.py /path/to/your/.bash_history
```

## How It Works

1.  **Parsing**: The tool reads the history file line by line. It ignores timestamps (lines starting with `#`) and lines starting with a space (often used in bash to prevent recording commands).
2.  **Storage**: Parsed commands are stored in `bash_history.db`.
3.  **Analysis**:
    -   **Frequency**: Counts occurrences of full command strings.
    -   **Typos**: Compares low-frequency base commands against high-frequency ones using `difflib` to find single-character differences.
    -   **Aliases**: Filters for long, frequent commands.

## Project Structure

- `main.py`: CLI entry point and file parser.
- `db_manager.py`: Handles SQLite database operations.
- `analyzer.py`: Contains analysis logic (frequency, typos, aliases).
- `sample_history.txt`: A sample history file for testing purposes.
