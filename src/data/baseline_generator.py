"""
Baseline preprocessing module for student performance dataset.

This module provides functionality to generate a baseline dataset
by applying only minimal structural cleaning steps, preserving the
original distribution for data drift simulations.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


class BaselineGenerator:
    """Class responsible for generating minimally processed baseline datasets."""

    def __init__(
        self,
        input_path: str,
        output_path: str,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize BaselineGenerator.

        Args:
            input_path: Path to raw data CSV file
            output_path: Path where the baseline dataset will be saved
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

    def get_null_summary(self) -> pd.Series:
        """
        Get summary of null values in the dataset.

        Returns:
            Series with null counts per column
        """
        return self.df.isnull().sum()

    def save_baseline_data(self) -> Path:
        """
        Save baseline dataset to output path.

        Returns:
            Path to saved file
        """
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(self.output_path, index=False)

        self.logger.info(
            f"Baseline dataset saved to: {self.output_path}\n"
            f"Shape: {self.df.shape[0]} rows, {self.df.shape[1]} columns"
        )

        return self.output_path

    def run_pipeline(self) -> pd.DataFrame:
        """
        Execute the baseline generation pipeline.

        Returns:
            Baseline DataFrame
        """
        self.logger.info("=" * 70)
        self.logger.info("Starting baseline generation pipeline")
        self.logger.info("=" * 70)

        # Load data
        self.load_data()

        # Normalize case
        self.normalize_case()

        # Trim whitespace
        self.trim_whitespace()

        # Replace null string patterns with NaN
        self.replace_null_strings()

        # Rename columns for consistency
        self.rename_columns({"Class_ X_Percentage": "Class_X_Percentage"})

        # Final summary
        null_summary = self.get_null_summary()
        self.logger.info("Null summary (no imputations applied):")
        self.logger.info(null_summary)

        self.logger.info("=" * 70)
        self.logger.info("Baseline generation pipeline completed")
        self.logger.info("=" * 70)

        return self.df


def main():
    """Main function to run baseline pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate baseline dataset")
    parser.add_argument(
        "--input",
        type=str,
        default="data/raw/student_entry_performance.csv",
        help="Path to raw data CSV file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/baseline/student_performance_baseline.csv",
        help="Path to save baseline dataset CSV file",
    )

    args = parser.parse_args()

    baseline = BaselineGenerator(input_path=args.input, output_path=args.output)
    baseline.run_pipeline()
    baseline.save_baseline_data()

    print("\n" + "=" * 70)
    print("Baseline dataset generated successfully")
    print("=" * 70)
    print(f"Output saved to: {args.output}")
    print("=" * 70)


if __name__ == "__main__":
    main()
