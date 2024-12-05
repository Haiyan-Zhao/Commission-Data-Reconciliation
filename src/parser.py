from abc import ABC, abstractmethod
import pandas as pd
from typing import Any
from .schema_mappings import SCHEMA_MAPPINGS

PARSER_MAP = {}

# Decorator to register a parser class in the PARSER_MAP.
def add_parser(identifier: str):
    def decorator(cls):
        PARSER_MAP[identifier] = cls
        return cls

    return decorator


class BaseParser(ABC):
    """
    Abstract base class for carrier-specific parsers.
    Each parser must implement `_parse_impl` and `carrier_name`.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_excel(self) -> pd.DataFrame:
        return pd.read_excel(self.file_path)

    @property
    def carrier_name(self) -> str:
        pass
    
    @property
    def column_mapping(self):
        return SCHEMA_MAPPINGS[self.carrier_name]

    def get_commission_period(self, df: pd.DataFrame) -> str:
        commission_period_mapping = "commission_period"
        pay_period = df[commission_period_mapping].dropna()

        date_obj = pd.to_datetime(pay_period, errors="coerce")
        return date_obj.dt.strftime("%Y-%m")

    # Clean and map a column based on the provided source.
    def _clean_column(self, df: pd.DataFrame, source: Any) -> pd.Series:
        if isinstance(source, str):
            return df[source] if source in df else pd.Series(None, index=df.index)
        elif callable(source):
            return source(df)
        else:
            return pd.Series(None, index=df.index)

    @abstractmethod
    def _parse_impl(self) -> pd.DataFrame:
        pass

    # Parse the file and map it to the standard schema.
    def parse(self) -> pd.DataFrame:
        carrier_name = self.carrier_name
        print(f"Parsing {carrier_name} data from file: {self.file_path}")

        # Read and map columns
        df = self.read_excel()
        parsed_df = self._parse_impl(df)

        # Add standard fields
        parsed_df["carrier_name"] = carrier_name
        parsed_df["commission_period"] = self.get_commission_period(parsed_df)

        return parsed_df

# Parser implementations for specific carriers
@add_parser("Centene")
class CenteneParser(BaseParser):
    
    @property
    def carrier_name(self) -> str:
        return "Centene"
    
    def _parse_impl(self, df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            {
                key: self._clean_column(df, source)
                for key, source in self.column_mapping.items()
            }
        )


# Parser for Emblem
@add_parser("Emblem")
class EmblemParser(BaseParser):
    @property
    def carrier_name(self) -> str:
        return "Emblem"
    def _parse_impl(self, df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            {
                key: self._clean_column(df, source)
                for key, source in self.column_mapping.items()
            }
        )


# Parser for Healthfirst
@add_parser("Healthfirst")
class HealthfirstParser(BaseParser):
    @property
    def carrier_name(self) -> str:
        return "Healthfirst"
    
    # Override to handle Healthfirst-specific date format.
    def get_commission_period(self, df: pd.DataFrame) -> str:
        pay_period = df["commission_period"].dropna()
        date_obj = pd.to_datetime(pay_period, format="%m/%Y", errors="coerce")
        return date_obj.dt.strftime("%Y-%m")
    
    def _parse_impl(self, df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            {
                key: self._clean_column(df, source)
                for key, source in self.column_mapping.items()
            }
        )
