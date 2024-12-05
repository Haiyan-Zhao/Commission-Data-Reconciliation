
import pandas as pd
from pathlib import Path
from src.parser import PARSER_MAP
from src.cleaner import DataCleaner
from src.analyzer import CommissionAnalyzer
from src.analyzer import TARGET_PERIOD
from src.analyzer import TOP_N
import fire
from src.constants import INPUT_DIRECTORY, OUTPUT_DIRECTORY, RESULT_FILE_NAME
from src.schema_mappings import SCHEMA_MAPPINGS


# Parse raw commission data for a specific carrier using its parser.
def parse_carrier_data(parser_class, file_path):
    print("Starting data parsering......")
    print(f"Parsing data using {parser_class.__name__}:")
    parser = parser_class(str(file_path))

    parsed_data = parser.parse()

    print(f"Parsed {len(parsed_data)} records from {file_path.name}.")
    return parsed_data

# Summarize the results of parsing multiple files.
def summarize_parsing_results(data_frames):
    total_records = sum(len(df) for df in data_frames)
    print(f"\nParsing finished! Total records: {total_records}")
    
    for i, df in enumerate(data_frames, start=1):
        print(f"Source {i}: {len(df)} records.")


# Clean and normalize parsed commission data.
def clean_data(parsed_data_frames, output_dir):
    print("\nStarting data cleaning......")

    valid_data_frames = []

    # Iterate through each parsed DataFrame
    for i, df in enumerate(parsed_data_frames):
        print(f"Processing Data File {i+1}: Shape = {df.shape}")
        
        # Check if the DataFrame is not empty
        if df.empty:
            print(f"DataFrame {i+1} is empty. Skipping.")
            continue
        
        # Drop rows and columns that are completely empty
        cleaned_df = df.dropna(how="all").dropna(axis=1, how="all")
        
        if not cleaned_df.empty:
            print(f"DataFrame {i+1} is valid. Shape after cleaning: {cleaned_df.shape}")
            valid_data_frames.append(cleaned_df)
        else:
            print(f"DataFrame {i+1} contains only NaN values after cleaning. Skipping.")

    if not valid_data_frames:
        raise ValueError("No valid DataFrames to process.") # Raise error if all DataFrames are invalid

    # Merge all valid parsed data into a single DataFrame
    combined_data = pd.concat(valid_data_frames, ignore_index=True)
    print(f"Combined data shape: {combined_data.shape}")
    print(f"Combined data columns: {combined_data.columns.tolist()}")

    # Clean and normalize the data
    data_cleaner = DataCleaner(combined_data)
    cleaned_data = data_cleaner.overall_clean()

    # Save cleaned data to a CSV file
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / RESULT_FILE_NAME
    cleaned_data.to_csv(output_path, index=False)
    print(f"Parsing finished! Cleaned data saved to {output_path}.")

    return cleaned_data

# Perform analysis on cleaned commission data, including summaries and top agent identification.
def analyze_commission_data(cleaned_data):

    print("\nStarting data analysis......")
    
    # Initialize the analyzer with cleaned data
    analyzer = CommissionAnalyzer(cleaned_data)

    # Generate a summary for the specified period
    period_summary = analyzer.generate_period_summary()
    print("\nPeriod Summary:")
    for key, value in period_summary.items():
        print(f"- {key}: {value}")

    # Identify the top N earning agents for the specified period
    top_agents = analyzer.calculate_top_earning_agents()
    
    print(f"\nTop {TOP_N} earning agents for period {TARGET_PERIOD}:")
 
    for idx, row in top_agents.iterrows():
        print(f"{idx + 1}. {row['agent_name']}: ${row['total_commission']:.2f}")

# Main pipeline to parse, clean, and analyze commission data.
def process_final(input_dir = INPUT_DIRECTORY, output_dir = OUTPUT_DIRECTORY):

    input_dir = Path(input_dir)
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    # Locate raw data files for each carrier
    raw_files = [
        input_dir / f"{carrier} 06.2024 Commission.xlsx"
        for carrier in SCHEMA_MAPPINGS.keys()
    ]

    parsed_data_frames = [] # Store parsed data for each file
    for file_path in raw_files:
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue

        # Match the appropriate parser class to the file
        parser_class = next((cls for name, cls in PARSER_MAP.items() if name in file_path.name), None)
        if not parser_class:
            print(f"No parser found for file: {file_path.name}")
            continue

        # Parse the file and store the result
        parsed_data = parse_carrier_data(parser_class, file_path)
        parsed_data_frames.append(parsed_data)

    # Summarize the results of parsing
    summarize_parsing_results(parsed_data_frames)

    # Clean and normalize the parsed data
    cleaned_data = clean_data(parsed_data_frames, output_dir)

    # Perform analysis on the cleaned data
    analyze_commission_data(cleaned_data)

    print("\nALL DONE!")


if __name__ == "__main__":
    fire.Fire()
