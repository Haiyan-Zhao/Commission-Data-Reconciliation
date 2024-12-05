from pathlib import Path

# Default commission period for analysis
TARGET_PERIOD = "2024-06"

# Number of top agents to display
TOP_N = 10

# Threshold for name similarity when deduplicating names
SIMILARITY_THRESHOLD = 0.9

# Columns related to IDs that need to be cleaned
ID_COLUMNS = [
    "agent_id",
    "agency_id",
]

# Columns related to dates that need to be cleaned
DATE_COLUMNS = [
    "effective_date",
    "term_date",
]

# Directory paths for input and output data
INPUT_DIRECTORY: Path = Path("data/original")
OUTPUT_DIRECTORY: Path = Path("data/result")

# File name for saving cleaned results
RESULT_FILE_NAME: str = "cleaned_commissions.csv"