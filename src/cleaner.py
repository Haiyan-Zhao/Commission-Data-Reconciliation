from difflib import SequenceMatcher
import pandas as pd
from .constants import SIMILARITY_THRESHOLD, ID_COLUMNS, DATE_COLUMNS


# This class is responsible for cleaning and normalizing raw commission data.
class DataCleaner:

    def __init__(self, df: pd.DataFrame):
        self.data = df.copy()
        self.cleaned_data = None
    
    # Convert to YYYY-MM-DD format
    def clean_dates(self) -> None:
        for col in DATE_COLUMNS:
            if col in self.data.columns:
                self.data[col] = pd.to_datetime(
                    self.data[col], format="mixed", errors="coerce"
                ).dt.strftime("%Y-%m-%d")
           

    # Standardize commission amount values, handling various formats and missing data.
    def clean_amounts(self) -> None:
        def clean_amount(val):
            if pd.isna(val):
                return 0.0

            if isinstance(val, (int, float)):
                return float(val)

            if isinstance(val, str):
                val = val.replace("$", "").replace(",", "").strip()
                if val.startswith("(") and val.endswith(")"):
                    val = "-" + val[1:-1]
                if val.startswith("-$"):
                    val = "-" + val[2:]
                return float(val)

        self.data["commission_amount"] = (
            self.data["commission_amount"].apply(clean_amount).astype(float)
        )

    # Standardize agent and agency names.
    def clean_names(self) -> None:

        def clean_name(name):
            if pd.isna(name) or not str(name).strip():
                return "Unknown-Name"
            name = str(name).strip()
            name = " ".join(word.capitalize() for word in name.split())
            return name

        if "agent_name" in self.data.columns:
            self.data["agent_name"] = self.data["agent_name"].apply(clean_name)
        if "agency_name" in self.data.columns:
            self.data["agency_name"] = self.data["agency_name"].apply(
                clean_name)
            
    # Deduplicate agent names using a similarity threshold.
    def deduplicate_names(self) -> None:
        if "agent_id" in self.data.columns and "agent_name" in self.data.columns:
            id_to_name = {}

            def find_closest_match(name, name_pool):
                # Find the closest matching name in the pool.
                best_match = None
                highest_ratio = 0
                for candidate in name_pool:
                    ratio = SequenceMatcher(None, name, candidate).ratio()
                    if ratio > highest_ratio:
                        highest_ratio = ratio
                        best_match = candidate
                return best_match, highest_ratio

            for _, row in self.data.iterrows():
                agent_id = row["agent_id"]
                agent_name = row["agent_name"]

                if pd.notna(agent_id) and agent_id not in id_to_name:
                    # Assign the first name for the ID
                    id_to_name[agent_id] = agent_name
                elif pd.notna(agent_id):
                    # Merge names for the same ID
                    closest_match, similarity = find_closest_match(
                        agent_name, [id_to_name[agent_id]])
                    if similarity >= SIMILARITY_THRESHOLD:
                        id_to_name[agent_id] = closest_match

            # Replace names in the DataFrame based on ID mapping
            self.data["agent_name"] = self.data.apply(
                lambda row: id_to_name.get(row["agent_id"], row["agent_name"]), axis=1
            )

            # Handle cases without ID based on similarity
            unique_names = set(self.data["agent_name"].dropna().unique())
            name_mapping = {}
            for name in unique_names:
                closest_match, similarity = find_closest_match(
                    name, unique_names - {name})
                if similarity >= SIMILARITY_THRESHOLD:
                    name_mapping[name] = closest_match
                else:
                    name_mapping[name] = name

            self.data["agent_name"] = self.data["agent_name"].map(name_mapping)


    # Clean and standardize agent_id and agency_id columns
    def clean_ids(self) -> None:

        for col in ID_COLUMNS:
            if col in self.data.columns:
                self.data[col] = (
                    self.data[col]
                    .astype(str)
                    .str.strip()
                    .str.replace(r"[^a-zA-Z0-9]", "", regex=True)
                )

    # Execute all cleaning steps on the data.
    def overall_clean(self) -> pd.DataFrame:
        self.clean_dates()
        self.clean_amounts()
        self.clean_names()
        self.deduplicate_names()
        self.cleaned_data = self.data

        return self.cleaned_data

