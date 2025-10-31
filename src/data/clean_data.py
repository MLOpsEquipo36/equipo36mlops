"""
Data cleaning module for student performance dataset.

This module provides functionality to clean and preprocess raw data,
following EDA best practices and handling missing values, duplicates,
and data standardization.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


class DataCleaner:
    """Class responsible for cleaning and preprocessing raw datasets."""

    def __init__(
        self,
        input_path: str,
        output_path: str,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize DataCleaner.

        Args:
            input_path: Path to raw data CSV file
            output_path: Path where cleaned data will be saved
            logger: Optional logger instance for tracking operations
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.logger = logger or self._setup_logger()
        self.df_raw: Optional[pd.DataFrame] = None
        self.df: Optional[pd.DataFrame] = None

        # Columns to apply uppercase and trim operations
        self.columns_to_normalize = [
            "Performance",
            "Gender",
            "Caste",
            "coaching",
            "time",
            "Class_ten_education",
            "twelve_education",
            "medium",
            "Class_ X_Percentage",
            "Class_XII_Percentage",
            "Father_occupation",
            "Mother_occupation",
            "mixed_type_col",
        ]

    @staticmethod
    def _setup_logger() -> logging.Logger:
        """Setup default logger for the class."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "[%(asctime)s | %(levelname)s] %(name)s -> %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def load_data(self) -> pd.DataFrame:
        """
        Load raw data from CSV file.

        Returns:
            DataFrame with raw data
        """
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        self.logger.info(f"Loading data from: {self.input_path}")
        self.df_raw = pd.read_csv(self.input_path)
        self.df = self.df_raw.copy()

        self.logger.info(
            f"Dataset loaded: {self.df.shape[0]} rows, {self.df.shape[1]} columns"
        )
        return self.df

    def normalize_case(self) -> pd.DataFrame:
        """
        Convert string columns to uppercase for consistency.

        Returns:
            DataFrame with normalized case
        """
        self.logger.info("Normalizing case: converting to uppercase")
        for col in self.columns_to_normalize:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.upper()
        return self.df

    def trim_whitespace(self) -> pd.DataFrame:
        """
        Remove leading/trailing whitespace from string columns.

        Returns:
            DataFrame with trimmed strings
        """
        self.logger.info("Trimming whitespace from string columns")
        for col in self.columns_to_normalize:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()
        return self.df

    def replace_null_strings(self) -> pd.DataFrame:
        """
        Replace common null string representations with NaN.

        Returns:
            DataFrame with null strings replaced
        """
        self.logger.info("Replacing null string representations with NaN")
        null_strings = ["NAN", "NaN", "nan", "NULL", "NONE", " "]
        self.df = self.df.replace(null_strings, np.nan)
        return self.df

    def handle_target_nulls(self, target_column: str = "Performance") -> pd.DataFrame:
        """
        Drop rows where target variable is null.

        Args:
            target_column: Name of the target column

        Returns:
            DataFrame with target nulls removed
        """
        initial_rows = len(self.df)
        self.df = self.df.dropna(subset=[target_column])
        dropped = initial_rows - len(self.df)

        if dropped > 0:
            self.logger.info(
                f"Dropped {dropped} rows with null target ({target_column})"
            )

        return self.df

    def drop_uninformative_columns(self, columns: List[str]) -> pd.DataFrame:
        """
        Drop columns that don't provide useful information.

        Args:
            columns: List of column names to drop

        Returns:
            DataFrame with specified columns removed
        """
        columns_to_drop = [col for col in columns if col in self.df.columns]
        if columns_to_drop:
            self.logger.info(f"Dropping columns: {columns_to_drop}")
            self.df = self.df.drop(columns=columns_to_drop)
        return self.df

    def rename_columns(self, rename_dict: Dict[str, str]) -> pd.DataFrame:
        """
        Rename columns for better consistency.

        Args:
            rename_dict: Dictionary mapping old names to new names

        Returns:
            DataFrame with renamed columns
        """
        self.df = self.df.rename(columns=rename_dict)
        self.logger.info(f"Renamed columns: {rename_dict}")
        return self.df

    def fill_ordinal_nulls_with_mode(
        self, columns: List[str], fill_value: str = "EXCELLENT"
    ) -> pd.DataFrame:
        """
        Fill null values in ordinal columns with a default value.

        Args:
            columns: List of ordinal column names
            fill_value: Default value to use for filling

        Returns:
            DataFrame with filled ordinal columns
        """
        for col in columns:
            if col in self.df.columns:
                initial_nulls = self.df[col].isnull().sum()
                if initial_nulls > 0:
                    self.df[col] = self.df[col].fillna(fill_value)
                    self.logger.info(
                        f"Filled {initial_nulls} nulls in {col} with '{fill_value}'"
                    )
        return self.df

    def fill_nominal_nulls_with_mode(self, column_mode_map: Dict[str, str]) -> pd.DataFrame:
        """
        Fill null values in nominal columns with their respective modes.

        Args:
            column_mode_map: Dictionary mapping column names to mode values

        Returns:
            DataFrame with filled nominal columns
        """
        for col, mode_value in column_mode_map.items():
            if col in self.df.columns:
                initial_nulls = self.df[col].isnull().sum()
                if initial_nulls > 0:
                    self.df[col] = self.df[col].fillna(mode_value)
                    self.logger.info(
                        f"Filled {initial_nulls} nulls in {col} with '{mode_value}'"
                    )
        return self.df

    def handle_gender_nulls(self, fill_value: str = "MISSING") -> pd.DataFrame:
        """
        Fill null gender values with a special 'MISSING' category.

        Args:
            fill_value: Value to use for missing gender

        Returns:
            DataFrame with gender nulls filled
        """
        if "Gender" in self.df.columns:
            initial_nulls = self.df["Gender"].isnull().sum()
            if initial_nulls > 0:
                self.df["Gender"] = self.df["Gender"].fillna(fill_value)
                self.logger.info(
                    f"Filled {initial_nulls} nulls in Gender with '{fill_value}'"
                )
        return self.df

    def get_null_summary(self) -> pd.Series:
        """
        Get summary of null values in the dataset.

        Returns:
            Series with null counts per column
        """
        return self.df.isnull().sum()

    def save_cleaned_data(self) -> Path:
        """
        Save cleaned dataset to output path.

        Returns:
            Path to saved file
        """
        # Create output directory if it doesn't exist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        self.df.to_csv(self.output_path, index=False)

        self.logger.info(
            f"Cleaned dataset saved to: {self.output_path}\n"
            f"Shape: {self.df.shape[0]} rows, {self.df.shape[1]} columns"
        )

        if self.df_raw is not None:
            reduction = len(self.df_raw) - len(self.df)
            self.logger.info(f"Reduction: {len(self.df_raw)} -> {len(self.df)} rows ({reduction} dropped)")

        return self.output_path

    def run_pipeline(self) -> pd.DataFrame:
        """
        Execute the complete data cleaning pipeline.

        Returns:
            Cleaned DataFrame
        """
        self.logger.info("=" * 70)
        self.logger.info("Starting data cleaning pipeline")
        self.logger.info("=" * 70)

        # Load data
        self.load_data()

        # Normalize case
        self.normalize_case()

        # Trim whitespace
        self.trim_whitespace()

        # Replace null strings
        self.replace_null_strings()

        # Handle target nulls (drop rows)
        self.handle_target_nulls()

        # Drop uninformative columns
        self.drop_uninformative_columns(["mixed_type_col"])

        # Rename columns for consistency
        self.rename_columns({"Class_ X_Percentage": "Class_X_Percentage"})

        # Fill ordinal nulls
        ordinal_cols = ["Class_X_Percentage", "Class_XII_Percentage"]
        self.fill_ordinal_nulls_with_mode(ordinal_cols)

        # Fill gender nulls with special category
        self.handle_gender_nulls()

        # Fill other nominal nulls with modes
        nominal_modes = {
            "Caste": "GENERAL",
            "coaching": "WA",
            "time": "TWO",
            "Class_ten_education": "SEBA",
            "twelve_education": "AHSEC",
            "medium": "ENGLISH",
            "Father_occupation": "OTHERS",
            "Mother_occupation": "HOUSE_WIFE",
        }
        self.fill_nominal_nulls_with_mode(nominal_modes)

        # Final validation
        null_summary = self.get_null_summary()
        if null_summary.sum() > 0:
            self.logger.warning(f"Warning: {null_summary.sum()} null values remaining")
            self.logger.warning(null_summary[null_summary > 0])
        else:
            self.logger.info("✅ No null values remaining")

        self.logger.info("=" * 70)
        self.logger.info("Data cleaning pipeline completed")
        self.logger.info("=" * 70)

        return self.df


def main():
    """Main function to run data cleaning pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Clean student performance dataset")
    parser.add_argument(
        "--input",
        type=str,
        default="data/raw/student_entry_performance.csv",
        help="Path to raw data CSV file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/student_performance.csv",
        help="Path to save cleaned data CSV file",
    )

    args = parser.parse_args()

    cleaner = DataCleaner(input_path=args.input, output_path=args.output)
    cleaner.run_pipeline()
    cleaner.save_cleaned_data()

    print("\n" + "=" * 70)
    print("✅ Data cleaning completed successfully!")
    print("=" * 70)
    print(f"📂 Output saved to: {args.output}")
    print("=" * 70)


if __name__ == "__main__":
    main()

