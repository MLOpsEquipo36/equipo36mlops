"""
Feature engineering module for student performance dataset.

This module provides functionality for feature selection, encoding,
and dimensionality reduction using statistical tests and PCA.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, spearmanr
from sklearn.decomposition import PCA
from sklearn.preprocessing import OneHotEncoder


class FeatureBuilder:
    """Class responsible for feature engineering and selection."""

    def __init__(
        self,
        input_path: str,
        output_path: str,
        encoder_dir: str = "models/encoders",
        preprocessor_dir: str = "models/preprocessors",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize FeatureBuilder.

        Args:
            input_path: Path to cleaned data CSV file
            output_path: Path where processed features will be saved
            encoder_dir: Directory to save encoders
            preprocessor_dir: Directory to save preprocessors
            logger: Optional logger instance for tracking operations
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.encoder_dir = Path(encoder_dir)
        self.preprocessor_dir = Path(preprocessor_dir)
        self.logger = logger or self._setup_logger()
        self.df: Optional[pd.DataFrame] = None

        # Define variable types
        self.nominal_variables = [
            "Gender",
            "Caste",
            "coaching",
            "time",
            "Class_ten_education",
            "twelve_education",
            "medium",
            "Father_occupation",
            "Mother_occupation",
        ]

        self.ordinal_variables = [
            "Class_X_Percentage",
            "Class_XII_Percentage",
        ]

        self.target_variable = "Performance"

        # Ordinal mappings
        self.ordinal_mapping = {
            "Class_X_Percentage": {
                "EXCELLENT": 3,
                "VG": 2,
                "GOOD": 1,
                "AVERAGE": 0,
            },
            "Class_XII_Percentage": {
                "EXCELLENT": 3,
                "VG": 2,
                "GOOD": 1,
                "AVERAGE": 0,
            },
        }

        self.target_mapping = {
            "EXCELLENT": 3,
            "VG": 2,
            "GOOD": 1,
            "AVERAGE": 0,
        }

        # Artifacts
        self.onehot_encoder: Optional[OneHotEncoder] = None
        self.pca_model: Optional[PCA] = None

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
        Load cleaned data from CSV file.

        Returns:
            DataFrame with cleaned data
        """
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        self.logger.info(f"Loading cleaned data from: {self.input_path}")
        self.df = pd.read_csv(self.input_path)

        self.logger.info(
            f"Dataset loaded: {self.df.shape[0]} rows, {self.df.shape[1]} columns"
        )
        return self.df

    def check_dominance(self, threshold: float = 0.85) -> Dict[str, float]:
        """
        Check for variables with dominant values above threshold.

        Args:
            threshold: Maximum frequency of most common value (default: 0.85)

        Returns:
            Dictionary mapping column names to their dominant value frequency
        """
        self.logger.info(f"Checking for dominant values (threshold: {threshold})")
        dominance_results = {}

        for col in self.df.columns:
            value_counts = self.df[col].value_counts(normalize=True)
            most_common_freq = value_counts.iloc[0]
            dominance_results[col] = most_common_freq

            if most_common_freq >= threshold:
                self.logger.warning(
                    f"{col}: {most_common_freq:.3f} - Consider removing (>= {threshold})"
                )

        return dominance_results

    def select_nominal_features(
        self, alpha: float = 0.05, min_cramers_v: float = 0.1
    ) -> List[str]:
        """
        Select nominal features using Chi-square test and Cramer's V.

        Args:
            alpha: Significance level for Chi-square test
            min_cramers_v: Minimum Cramer's V threshold

        Returns:
            List of selected nominal feature names
        """
        self.logger.info("Performing feature selection for nominal variables")
        self.logger.info(f"Criteria: p-value < {alpha}, Cramer's V >= {min_cramers_v}")

        selected_features = []

        for var in self.nominal_variables:
            if var not in self.df.columns:
                continue

            contingency_table = pd.crosstab(self.df[var], self.df[self.target_variable])
            chi2, p_value, dof, expected = chi2_contingency(contingency_table)

            n = contingency_table.sum().sum()
            cramers_v = np.sqrt(chi2 / (n * (min(contingency_table.shape) - 1)))

            self.logger.info(
                f"{var} vs {self.target_variable}: "
                f"p-value={p_value:.6f}, Cramer's V={cramers_v:.3f}"
            )

            if p_value < alpha and cramers_v >= min_cramers_v:
                selected_features.append(var)
                self.logger.info(f"  ✅ {var} selected")
            else:
                self.logger.info(f"  ❌ {var} rejected")

        return selected_features

    def select_ordinal_features(
        self, alpha: float = 0.05, min_correlation: float = 0.1
    ) -> List[str]:
        """
        Select ordinal features using Spearman correlation.

        Args:
            alpha: Significance level for correlation test
            min_correlation: Minimum absolute correlation threshold

        Returns:
            List of selected ordinal feature names
        """
        self.logger.info("Performing feature selection for ordinal variables")
        self.logger.info(
            f"Criteria: p-value < {alpha}, |correlation| >= {min_correlation}"
        )

        selected_features = []

        # Encode ordinal variables temporarily
        df_encoded = self.df.copy()
        for col in self.ordinal_variables:
            if col in df_encoded.columns:
                df_encoded[f"{col}_encoded"] = df_encoded[col].map(
                    self.ordinal_mapping[col]
                )

        df_encoded["Performance_encoded"] = df_encoded[self.target_variable].map(
            self.target_mapping
        )

        for col in self.ordinal_variables:
            if col not in df_encoded.columns:
                continue

            col_encoded = f"{col}_encoded"
            correlation, p_value = spearmanr(
                df_encoded[col_encoded],
                df_encoded["Performance_encoded"],
                nan_policy="omit",
            )

            self.logger.info(
                f"{col} vs {self.target_variable}: "
                f"correlation={correlation:.3f}, p-value={p_value:.6f}"
            )

            if p_value < alpha and abs(correlation) >= min_correlation:
                selected_features.append(col)
                self.logger.info(f"  ✅ {col} selected")
            else:
                self.logger.info(f"  ❌ {col} rejected")

        return selected_features

    def onehot_encode(
        self, nominal_features: List[str], drop_original: bool = True
    ) -> pd.DataFrame:
        """
        Apply OneHot encoding to nominal features.

        Args:
            nominal_features: List of nominal feature names to encode
            drop_original: Whether to drop original columns after encoding

        Returns:
            DataFrame with encoded features
        """
        self.logger.info(f"Applying OneHot encoding to {len(nominal_features)} features")

        # Filter features that exist in dataframe
        features_to_encode = [f for f in nominal_features if f in self.df.columns]

        if not features_to_encode:
            self.logger.warning("No valid nominal features to encode")
            return self.df

        # Initialize and fit encoder
        self.onehot_encoder = OneHotEncoder(sparse_output=False, drop="first")
        onehot_encoded = self.onehot_encoder.fit_transform(self.df[features_to_encode])

        # Get feature names
        onehot_feature_names = self.onehot_encoder.get_feature_names_out(
            features_to_encode
        )

        # Create DataFrame with encoded features
        onehot_df = pd.DataFrame(
            onehot_encoded, columns=onehot_feature_names, index=self.df.index
        )

        # Combine with original dataframe
        if drop_original:
            df_result = self.df.drop(columns=features_to_encode)
        else:
            df_result = self.df.copy()

        df_result = pd.concat([df_result, onehot_df], axis=1)

        self.logger.info(
            f"OneHot encoding complete: {len(onehot_feature_names)} new features created"
        )

        return df_result

    def apply_pca(
        self, variance_threshold: float = 0.95, exclude_target: bool = True
    ) -> pd.DataFrame:
        """
        Apply PCA for dimensionality reduction.

        Args:
            variance_threshold: Minimum variance to retain (0-1)
            exclude_target: Whether to exclude target variable from PCA

        Returns:
            DataFrame with PCA components
        """
        self.logger.info(
            f"Applying PCA to retain {variance_threshold*100:.1f}% of variance"
        )

        # Prepare features for PCA
        if exclude_target:
            feature_cols = [
                col
                for col in self.df.columns
                if col not in [self.target_variable, "Performance_encoded"]
            ]
            X = self.df[feature_cols].values
        else:
            X = self.df.drop(columns=[self.target_variable], errors="ignore").values

        # Fit PCA
        self.pca_model = PCA(n_components=variance_threshold)
        X_pca = self.pca_model.fit_transform(X)

        # Calculate explained variance
        explained_variance = self.pca_model.explained_variance_ratio_.sum()

        self.logger.info(
            f"PCA complete: {X_pca.shape[1]} components explain "
            f"{explained_variance:.1%} of variance"
        )

        # Create DataFrame with PCA components
        pca_columns = [f"PC{i+1}" for i in range(X_pca.shape[1])]
        df_pca = pd.DataFrame(X_pca, columns=pca_columns, index=self.df.index)

        # Add target if it exists
        if self.target_variable in self.df.columns:
            df_pca[self.target_variable] = self.df[self.target_variable].values
        elif "Performance_encoded" in self.df.columns:
            df_pca["Performance"] = self.df["Performance_encoded"].values

        return df_pca

    def encode_ordinal_target(self) -> pd.DataFrame:
        """
        Encode ordinal target variable.

        Returns:
            DataFrame with encoded target
        """
        if self.target_variable in self.df.columns:
            self.df["Performance_encoded"] = self.df[self.target_variable].map(
                self.target_mapping
            )
        return self.df

    def save_artifacts(self) -> Tuple[Path, Path]:
        """
        Save encoder and PCA model to disk.

        Returns:
            Tuple of (encoder_path, pca_path)
        """
        # Create directories if they don't exist
        self.encoder_dir.mkdir(parents=True, exist_ok=True)
        self.preprocessor_dir.mkdir(parents=True, exist_ok=True)

        encoder_path = self.encoder_dir / "onehot_encoder.pkl"
        pca_path = self.preprocessor_dir / "pca_model.pkl"

        if self.onehot_encoder is not None:
            joblib.dump(self.onehot_encoder, encoder_path)
            self.logger.info(f"Encoder saved to: {encoder_path}")
        else:
            self.logger.warning("No encoder to save")

        if self.pca_model is not None:
            joblib.dump(self.pca_model, pca_path)
            self.logger.info(f"PCA model saved to: {pca_path}")
        else:
            self.logger.warning("No PCA model to save")

        return encoder_path, pca_path

    def save_features(self) -> Path:
        """
        Save processed features to output path.

        Returns:
            Path to saved file
        """
        # Create output directory if it doesn't exist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        self.df.to_csv(self.output_path, index=False)

        self.logger.info(
            f"Processed features saved to: {self.output_path}\n"
            f"Shape: {self.df.shape[0]} rows, {self.df.shape[1]} columns"
        )

        return self.output_path

    def run_pipeline(
        self,
        feature_selection: bool = True,
        apply_encoding: bool = True,
        apply_pca: bool = True,
        variance_threshold: float = 0.95,
    ) -> pd.DataFrame:
        """
        Execute the complete feature engineering pipeline.

        Args:
            feature_selection: Whether to perform feature selection
            apply_encoding: Whether to apply OneHot encoding
            apply_pca: Whether to apply PCA
            variance_threshold: Variance threshold for PCA

        Returns:
            DataFrame with engineered features
        """
        self.logger.info("=" * 70)
        self.logger.info("Starting feature engineering pipeline")
        self.logger.info("=" * 70)

        # Load data
        self.load_data()

        # Check for dominant values
        self.check_dominance()

        # Feature selection
        if feature_selection:
            selected_nominal = self.select_nominal_features()
            selected_ordinal = self.select_ordinal_features()

            # Drop non-selected nominal features
            nominal_to_drop = set(self.nominal_variables) - set(selected_nominal)
            if nominal_to_drop:
                self.logger.info(f"Dropping non-selected nominal features: {nominal_to_drop}")
                self.df = self.df.drop(columns=list(nominal_to_drop))
                # Update nominal_variables
                self.nominal_variables = selected_nominal

            # Keep only selected ordinal features
            ordinal_to_drop = set(self.ordinal_variables) - set(selected_ordinal)
            if ordinal_to_drop:
                self.logger.info(f"Dropping non-selected ordinal features: {ordinal_to_drop}")
                # We'll keep them for now, but only use selected ones later

        # Encode target
        self.encode_ordinal_target()

        # OneHot encoding for nominal features
        if apply_encoding and self.nominal_variables:
            self.df = self.onehot_encode(self.nominal_variables, drop_original=True)

            # Drop original ordinal columns (keeping encoded versions if needed)
            cols_to_drop = self.ordinal_variables + [self.target_variable]
            cols_to_drop = [c for c in cols_to_drop if c in self.df.columns]
            self.df = self.df.drop(columns=cols_to_drop)

        # Apply PCA
        if apply_pca:
            self.df = self.apply_pca(variance_threshold=variance_threshold)

        self.logger.info("=" * 70)
        self.logger.info("Feature engineering pipeline completed")
        self.logger.info("=" * 70)

        return self.df


def main():
    """Main function to run feature engineering pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Build features for student performance dataset")
    parser.add_argument(
        "--input",
        type=str,
        default="data/processed/student_performance.csv",
        help="Path to cleaned data CSV file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/student_performance_features.csv",
        help="Path to save processed features CSV file",
    )
    parser.add_argument(
        "--encoder-dir",
        type=str,
        default="models/encoders",
        help="Directory to save encoders",
    )
    parser.add_argument(
        "--preprocessor-dir",
        type=str,
        default="models/preprocessors",
        help="Directory to save preprocessors",
    )
    parser.add_argument(
        "--variance-threshold",
        type=float,
        default=0.95,
        help="Variance threshold for PCA (default: 0.95)",
    )
    parser.add_argument(
        "--no-feature-selection",
        action="store_true",
        help="Skip feature selection step",
    )
    parser.add_argument(
        "--no-encoding",
        action="store_true",
        help="Skip OneHot encoding step",
    )
    parser.add_argument(
        "--no-pca",
        action="store_true",
        help="Skip PCA step",
    )

    args = parser.parse_args()

    builder = FeatureBuilder(
        input_path=args.input,
        output_path=args.output,
        encoder_dir=args.encoder_dir,
        preprocessor_dir=args.preprocessor_dir,
    )

    builder.run_pipeline(
        feature_selection=not args.no_feature_selection,
        apply_encoding=not args.no_encoding,
        apply_pca=not args.no_pca,
        variance_threshold=args.variance_threshold,
    )

    builder.save_features()
    builder.save_artifacts()

    print("\n" + "=" * 70)
    print("✅ Feature engineering completed successfully!")
    print("=" * 70)
    print(f"📂 Features saved to: {args.output}")
    print(f"📦 Encoders saved to: {args.encoder_dir}")
    print(f"📦 Preprocessors saved to: {args.preprocessor_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()

