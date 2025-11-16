"""
Inference Feature Pipeline (adjusted to match training logs).

This pipeline reproduces exactly the transformations applied during training:
- Uses the same selected nominal variables (6) that were used to fit the OneHotEncoder.
- Ensures one-hot feature names/order match encoder.get_feature_names_out(...)
- Ensures the PCA receives the same number of features (n_features_in_) it was trained on.
- Provides explicit, actionable errors if incoming data doesn't match expected schema.
"""

import logging
from pathlib import Path
from typing import Optional, List

import joblib
import numpy as np
import pandas as pd


class FeatureInferencePipelineAdjusted:
    def __init__(
        self,
        encoder_path: str,
        pca_path: str,
        ordinal_mapping: dict,
        nominal_variables: List[str],
        ordinal_variables: List[str],
        target_variable: str = "Performance",
        logger: Optional[logging.Logger] = None,
    ):
        self.encoder_path = Path(encoder_path)
        self.pca_path = Path(pca_path)

        self.ordinal_mapping = ordinal_mapping
        self.nominal_variables = list(nominal_variables)  # enforce list copy
        self.ordinal_variables = list(ordinal_variables)
        self.target_variable = target_variable
        self.target_mapping = {
            "EXCELLENT": 3,
            "VG": 2,
            "GOOD": 1,
            "AVERAGE": 0,
        }

        self.logger = logger or self._setup_logger()

        # Load artifacts
        self.encoder = self._load_encoder()
        self.pca = self._load_pca()

        # Get the actual feature names used during training from the encoder
        if hasattr(self.encoder, 'feature_names_in_'):
            # Use the feature names that were actually used during training
            self.nominal_variables = list(self.encoder.feature_names_in_)
            self.logger.info(f"Using encoder's feature_names_in_: {self.nominal_variables}")
        else:
            # Fallback: use provided nominal_variables
            self.logger.warning("Encoder doesn't have feature_names_in_, using provided nominal_variables")

        # Expected onehot feature names (determined from the encoder and nominal_variables)
        # We compute here so we can check/reorder at transform time.
        self.expected_onehot_names = list(self.encoder.get_feature_names_out(self.nominal_variables))
        self.logger.info(f"Expected onehot features count: {len(self.expected_onehot_names)}")

    @staticmethod
    def _setup_logger() -> logging.Logger:
        logger = logging.getLogger("InferencePipelineAdjusted")
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

    def _load_encoder(self):
        if not self.encoder_path.exists():
            raise FileNotFoundError(f"OneHot encoder not found at: {self.encoder_path}")
        self.logger.info(f"Loading OneHotEncoder from: {self.encoder_path}")
        enc = joblib.load(self.encoder_path)
        return enc

    def _load_pca(self):
        if not self.pca_path.exists():
            raise FileNotFoundError(f"PCA model not found at: {self.pca_path}")
        self.logger.info(f"Loading PCA model from: {self.pca_path}")
        pca = joblib.load(self.pca_path)
        # pca.n_features_in_ is expected to be the number of input features PCA was fit on (24)
        self.logger.info(f"PCA expects input features: {getattr(pca, 'n_features_in_', 'UNKNOWN')}")
        return pca

    # --- Helpers ---------------------------------------------------------
    def _check_nominal_columns_present(self, df: pd.DataFrame):
        missing = [c for c in self.nominal_variables if c not in df.columns]
        if missing:
            raise ValueError(
                "Input data is missing nominal columns required by the encoder: "
                f"{missing}. Provide these columns (even if empty) to ensure correct transform."
            )

    def _force_onehot_dataframe(self, onehot_df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure the onehot_df contains exactly the expected_onehot_names in that order.
        If any expected column is missing (rare), add it filled with zeros.
        If extra columns present, drop them.
        """
        cols_present = list(onehot_df.columns)
        # Add missing expected columns (fill with zeros)
        for c in self.expected_onehot_names:
            if c not in onehot_df.columns:
                self.logger.warning(f"OneHot produced missing column '{c}'. Filling with zeros.")
                onehot_df[c] = 0.0

        # Drop unexpected columns
        extras = [c for c in onehot_df.columns if c not in self.expected_onehot_names]
        if extras:
            self.logger.warning(f"OneHot produced extra columns {extras}. They will be dropped.")
            onehot_df = onehot_df.drop(columns=extras)

        # Reorder
        onehot_df = onehot_df[self.expected_onehot_names]
        return onehot_df

    # --- Transformation steps -------------------------------------------
    def encode_ordinal(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in self.ordinal_variables:
            if col in df.columns:
                df[f"{col}_encoded"] = df[col].map(self.ordinal_mapping.get(col, {}))
            else:
                self.logger.debug(f"Ordinal column '{col}' not in input; skipping encoding.")
        return df

    def apply_onehot(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform nominal variables using the pretrained encoder.
        Requires presence of nominal_variables in input dataframe.
        """
        df = df.copy()

        # Ensure required nominal columns exist
        self._check_nominal_columns_present(df)

        # Select nominal columns in the same order as during training
        X_nominal = df[self.nominal_variables]

        # Transform using the trained encoder (no fit)
        self.logger.info("Applying trained OneHotEncoder.transform()")
        try:
            onehot_arr = self.encoder.transform(X_nominal)
        except Exception as e:
            # Give a helpful error message
            raise RuntimeError(
                "OneHotEncoder.transform failed. Possible causes: encoder was trained with "
                "different categorical levels or the input contains unseen structure. "
                f"Original error: {e}"
            ) from e

        # Build DataFrame
        onehot_cols = list(self.encoder.get_feature_names_out(self.nominal_variables))
        onehot_df = pd.DataFrame(onehot_arr, columns=onehot_cols, index=df.index)

        # Guarantee exact expected columns & order
        onehot_df = self._force_onehot_dataframe(onehot_df)

        # Drop original nominal columns and concat onehot
        df = df.drop(columns=self.nominal_variables, errors="ignore")
        df = pd.concat([df, onehot_df], axis=1)

        self.logger.info(f"OneHot transformed. Resulting columns (sample): {onehot_df.columns.tolist()[:6]} ...")
        return df

    def apply_pca(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Drop target if present
        if self.target_variable in df.columns:
            df = df.drop(columns=[self.target_variable])

        # Build X from columns that PCA expects: PCA was trained on 'n_features_in_' features;
        # This includes both onehot features AND ordinal encoded features
        if hasattr(self.pca, "n_features_in_"):
            n_expected = int(self.pca.n_features_in_)
        else:
            n_expected = len(self.expected_onehot_names)  # fallback

        # Collect all features for PCA: onehot + ordinal encoded
        ordinal_encoded_cols = [f"{col}_encoded" for col in self.ordinal_variables]
        all_pca_features = self.expected_onehot_names + ordinal_encoded_cols

        # Ensure the DataFrame has the expected columns (pad with zeros if necessary)
        missing_for_pca = [c for c in all_pca_features if c not in df.columns]
        if missing_for_pca:
            self.logger.warning(f"Missing columns for PCA input: {missing_for_pca}. Filling with zeros.")
            for c in missing_for_pca:
                df[c] = 0.0

        # Select features in the correct order: onehot first, then ordinal encoded
        X = df[all_pca_features].values  # ensures order

        # Sanity check shape
        if X.shape[1] != n_expected:
            raise RuntimeError(
                f"Shape mismatch for PCA: PCA expects {n_expected} features but input has {X.shape[1]}.\n"
                f"Expected feature names (len={len(all_pca_features)}): {all_pca_features}"
            )

        # Transform with trained PCA
        self.logger.info("Applying trained PCA.transform()")
        X_pca = self.pca.transform(X)

        # Build DataFrame of PCs
        pc_cols = [f"PC{i + 1}" for i in range(X_pca.shape[1])]
        df_pca = pd.DataFrame(X_pca, columns=pc_cols, index=df.index)

        # If original input had target, keep it appended (useful for debugging)
        if self.target_variable in df.columns:
            # Note: target was dropped earlier; if you want to preserve original target pass it separately.
            pass

        return df_pca

    # --- Main method ---------------------------------------------------
    def transform(self, df: pd.DataFrame, apply_pca: bool = True) -> pd.DataFrame:
        """
        Full inference pipeline: ordinal → onehot → PCA

        If the dataset contains the target column (Performance),
        it will be reattached at the end of the final transformed output.
        """

        self.logger.info("Starting inference data transformation")

        df = df.copy()

        # ------------------------------------------------------------------
        # 1. Preserve target variable (if available)
        # ------------------------------------------------------------------
        target_series = None
        if self.target_variable in df.columns:
            target_series = df[self.target_variable].copy()
            df = df.drop(columns=[self.target_variable])
            self.logger.info("Target variable found and temporarily removed for processing.")

        # ------------------------------------------------------------------
        # 2. Ordinal encoding
        # ------------------------------------------------------------------
        df = self.encode_ordinal(df)

        # ------------------------------------------------------------------
        # 3. OneHot encoding
        # ------------------------------------------------------------------
        df = self.apply_onehot(df)

        # ------------------------------------------------------------------
        # 4. Remove original ordinal columns
        # ------------------------------------------------------------------
        drop_cols = [c for c in self.ordinal_variables if c in df.columns]
        df = df.drop(columns=drop_cols)

        # ------------------------------------------------------------------
        # 5. PCA (optional)
        # ------------------------------------------------------------------
        if apply_pca:
            df = self.apply_pca(df)

        # ------------------------------------------------------------------
        # 6. Reattach target (if available)
        # ------------------------------------------------------------------
        if target_series is not None:
            df[self.target_variable] = target_series.values
            df[self.target_variable] = df[self.target_variable].map(
                self.target_mapping
            )
            self.logger.info("Target variable reattached to final transformed data.")

        self.logger.info("Inference transformation completed")
        return df


# ----------------- CLI -----------------------------------------------------
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Adjusted Inference Feature Pipeline")
    parser.add_argument("--input", type=str, required=True, help="Path to new incoming CSV data")
    parser.add_argument("--output", type=str, required=True, help="Path to save transformed features")
    parser.add_argument("--encoder", type=str, default="models/encoders/onehot_encoder.pkl")
    parser.add_argument("--pca", type=str, default="models/preprocessors/pca_model.pkl")
    args = parser.parse_args()

    # Load encoder first to get the actual nominal variables it was trained on
    encoder_temp = joblib.load(args.encoder)
    if hasattr(encoder_temp, 'feature_names_in_'):
        # Use the actual variables the encoder was trained on
        nominal_vars = list(encoder_temp.feature_names_in_)
        print(f"Using encoder's feature_names_in_: {nominal_vars}")
    else:
        # Fallback: According to training logs, these were the selected nominal features
        nominal_vars = [
            "Caste",
            "coaching",
            "medium",
            "Father_occupation",
            "Mother_occupation",
        ]
        print(f"Encoder doesn't have feature_names_in_, using fallback: {nominal_vars}")

    # Ordinal vars (kept for parity; training did not include them into PCA)
    ordinal_vars = ["Class_X_Percentage", "Class_XII_Percentage"]

    ordinal_mapping = {
        "Class_X_Percentage": {"EXCELLENT": 3, "VG": 2, "GOOD": 1, "AVERAGE": 0},
        "Class_XII_Percentage": {"EXCELLENT": 3, "VG": 2, "GOOD": 1, "AVERAGE": 0},
    }

    pipeline = FeatureInferencePipelineAdjusted(
        encoder_path=args.encoder,
        pca_path=args.pca,
        ordinal_mapping=ordinal_mapping,
        nominal_variables=nominal_vars,
        ordinal_variables=ordinal_vars,
    )

    df_in = pd.read_csv(args.input)
    df_out = pipeline.transform(df_in, apply_pca=True)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(args.output, index=False)

    print("✅ Inference transformation saved to:", args.output)


if __name__ == "__main__":
    main()
