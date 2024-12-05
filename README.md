# Solution for Commission Data Reconciliation

## Project Overview

This project provides a solution for processing, cleaning, and analyzing insurance commission data for Field Marketing Organizations (FMOs) and agencies. It automates the handling of commission data from multiple carriers, normalizes it into a standardized format, and generates performance analytics and reports.


## Core Components

1. **Parsers** (`src/parser.py`)

   - `BaseParser`: Abstract base class defining the common parser interface
   - `CenteneParser`: Centene-specific data parser
   - `EmblemParser`: Emblem-specific data parser
   - `HealthfirstParser`: Healthfirst-specific data parser

2. **Data Cleaning** (`src/cleaner.py`)

   - `DataCleaner`: Cleans and normalizes commission data (e.g., date standardization, name deduplication)

3. **Data Analysis** (`src/analyzer.py`)

   - `CommissionAnalyzer`: Generates performance reports and analytics

4. **Constants and Schema** (`src/constants.py`, `src/schema_mappings.py`)

   - Centralized configurations for file paths, data schemas, and parsing rules


## Setup

1. Install required dependencies:
`pip install -r requirements.txt`
2. Set up pre-commit hooks (optional):
`pre-commit run --all-files`


## Running
1. Place the raw carrier data files in the data/original directory.
2. Run the pipeline:
`python main.py process_final`


## Expected Outputs

1. A cleaned and standardized commission data CSV file saved to the output directory (default: `data/result/cleaned_commissions.csv`).
2. Analytics:
   - Period summary of commission data
   - Top 10 agents by total earnings
3. Processing Statistics:
   - Summary of parsed records by source
   - Validation results and cleaning details
