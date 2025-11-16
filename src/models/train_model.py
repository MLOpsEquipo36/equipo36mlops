"""
Model training module for student performance prediction.

This module provides functionality for training, evaluating, and logging
machine learning models using MLflow for experiment tracking.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

from catboost import CatBoostRegressor
import lightgbm as lgb
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, root_mean_squared_error
from sklearn.model_selection import train_test_split
import xgboost as xgb


class ModelTrainer:
    """Class responsible for training and evaluating ML models."""

    def __init__(
        self,
        input_path: str,
        mlflow_dir: str = "data/mlflow",
        experiment_name: str = "mlflow-student-performance-experiment",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize ModelTrainer.

        Args:
            input_path: Path to features CSV file
            mlflow_dir: Directory for MLflow tracking
            experiment_name: Name of MLflow experiment
            logger: Optional logger instance for tracking operations
        """
        self.input_path = Path(input_path)
        self.mlflow_dir = Path(mlflow_dir)
        self.experiment_name = experiment_name
        self.logger = logger or self._setup_logger()

        # Configure MLflow
        mlflow.set_tracking_uri(f"file:{self.mlflow_dir}")
        self.mlflow_dir.mkdir(parents=True, exist_ok=True)

        # Data
        self.df: Optional[pd.DataFrame] = None
        self.X_train: Optional[pd.DataFrame] = None
        self.X_test: Optional[pd.DataFrame] = None
        self.y_train: Optional[pd.Series] = None
        self.y_test: Optional[pd.Series] = None

        # Models
        self.trained_models: Dict[str, any] = {}
        self.model_metrics: Dict[str, Dict[str, float]] = {}

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

    def load_data(self, target_column: str = "Performance") -> pd.DataFrame:
        """
        Load features data from CSV file.

        Args:
            target_column: Name of the target column

        Returns:
            DataFrame with features and target
        """
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        self.logger.info(f"Loading features from: {self.input_path}")
        self.df = pd.read_csv(self.input_path)

        self.logger.info(f"Dataset loaded: {self.df.shape[0]} rows, {self.df.shape[1]} columns")

        if target_column not in self.df.columns:
            raise ValueError(
                f"Target column '{target_column}' not found in dataset. "
                f"Available columns: {list(self.df.columns)}"
            )

        return self.df

    def split_data(
        self,
        target_column: str = "Performance",
        test_size: float = 0.2,
        random_state: int = 13,
        stratify: bool = True,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Split data into training and testing sets.

        Args:
            target_column: Name of the target column
            test_size: Proportion of data for testing
            random_state: Random seed for reproducibility
            stratify: Whether to stratify split by target

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        self.logger.info("Splitting data into train/test sets")

        X = self.df.drop(columns=[target_column])
        y = self.df[target_column]

        stratify_param = y if stratify else None

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify_param,
        )

        self.logger.info(
            f"Train set: {self.X_train.shape[0]} samples, "
            f"Test set: {self.X_test.shape[0]} samples"
        )

        return self.X_train, self.X_test, self.y_train, self.y_test

    def _setup_mlflow_experiment(self) -> str:
        """
        Setup MLflow experiment.

        Returns:
            Experiment ID
        """
        existing_experiment = mlflow.get_experiment_by_name(name=self.experiment_name)

        if existing_experiment is None:
            experiment_id = mlflow.create_experiment(
                name=self.experiment_name,
                tags={"owner": "equipo36", "project": "student-performance-prediction"},
            )
            self.logger.info(
                f"Created new MLflow experiment: '{self.experiment_name}' (ID: {experiment_id})"
            )
        else:
            experiment_id = existing_experiment.experiment_id
            self.logger.info(
                f"Using existing MLflow experiment: '{self.experiment_name}' (ID: {experiment_id})"
            )

        return experiment_id

    def evaluate_and_log_model(
        self,
        model_name: str,
        model: any,
        params: Optional[Dict] = None,
    ) -> Tuple[float, float]:
        """
        Train model, evaluate, and log to MLflow.

        Args:
            model_name: Name identifier for the model
            model: Untrained model instance
            params: Model parameters to log

        Returns:
            Tuple of (RMSE, QWK) metrics
        """
        self.logger.info(f"Training and evaluating model: {model_name}")

        experiment_id = self._setup_mlflow_experiment()

        with mlflow.start_run(experiment_id=experiment_id, run_name=model_name):
            # Log parameters
            if params:
                mlflow.log_params(params)
                self.logger.info(f"Logged parameters: {params}")

            # Train model
            model.fit(self.X_train, self.y_train)
            self.logger.info(f"Model '{model_name}' training complete")

            # Predict
            y_pred = model.predict(self.X_test)
            y_pred_class = np.rint(y_pred).astype(int)

            # Compute metrics
            rmse = root_mean_squared_error(self.y_test, y_pred_class)
            qwk = cohen_kappa_score(self.y_test, y_pred_class, weights="quadratic")

            # Log metrics
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("quadratic_weighted_kappa", qwk)

            self.logger.info(f"Metrics - RMSE: {rmse:.4f}, QWK: {qwk:.4f}")

            # Log model
            mlflow.sklearn.log_model(model, input_example=self.X_test.iloc[:5], artifact_path=model_name, registered_model_name=model_name)

            self.logger.info(
                f"Model '{model_name}' logged to MLflow under experiment '{self.experiment_name}'"
            )

            # Store trained model and metrics
            self.trained_models[model_name] = model
            self.model_metrics[model_name] = {"rmse": rmse, "qwk": qwk}

            return rmse, qwk

    def train_lightgbm(
        self,
        params: Optional[Dict] = None,
    ) -> Tuple[float, float]:
        """
        Train LightGBM model.

        Args:
            params: Model parameters (uses defaults if None)

        Returns:
            Tuple of (RMSE, QWK) metrics
        """
        if params is None:
            self.logger.info("No hyperparameters provided for LightGBM. Using default values.")
            params = {
                "objective": "regression",
                "metric": "rmse",
                "learning_rate": 0.05,
                "num_leaves": 31,
                "max_depth": -1,
                "min_data_in_leaf": 20,
                "feature_fraction": 0.8,
                "bagging_fraction": 0.8,
                "bagging_freq": 5,
                "verbose": -1,
                "random_state": 13,
            }

        model = lgb.LGBMRegressor(**params)
        return self.evaluate_and_log_model("LightGBM", model, params)

    def train_xgboost(
        self,
        params: Optional[Dict] = None,
    ) -> Tuple[float, float]:
        """
        Train XGBoost model.

        Args:
            params: Model parameters (uses defaults if None)

        Returns:
            Tuple of (RMSE, QWK) metrics
        """
        if params is None:
            self.logger.info("No hyperparameters provided for XGBoost. Using default values.")
            params = {
                "objective": "reg:squarederror",
                "n_estimators": 200,
                "learning_rate": 0.05,
                "max_depth": 6,
                "random_state": 13,
            }

        model = xgb.XGBRegressor(**params)
        return self.evaluate_and_log_model("XGBoost", model, params)

    def train_catboost(
        self,
        params: Optional[Dict] = None,
    ) -> Tuple[float, float]:
        """
        Train CatBoost model.

        Args:
            params: Model parameters (uses defaults if None)

        Returns:
            Tuple of (RMSE, QWK) metrics
        """
        if params is None:
            self.logger.info("No hyperparameters provided for CatBoost. Using default values.")
            params = {
                "iterations": 300,
                "learning_rate": 0.05,
                "depth": 6,
                "loss_function": "RMSE",
                "random_seed": 42,
            }

        model = CatBoostRegressor(**params)
        return self.evaluate_and_log_model("CatBoost", model, params)

    def train_all_models(
        self, hyperparameters: Optional[Dict[str, Dict[str, str | float]]] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Train all available models.

        Returns:
            Dictionary mapping model names to their metrics
        """
        self.logger.info("=" * 70)
        self.logger.info("Training all models")
        self.logger.info("=" * 70)

        # Train LightGBM
        self.train_lightgbm(params=hyperparameters.get("lightgbm") if hyperparameters else None)

        # Train XGBoost
        self.train_xgboost(params=hyperparameters.get("xgboost") if hyperparameters else None)

        # Train CatBoost
        self.train_catboost(params=hyperparameters.get("catboost") if hyperparameters else None)

        self.logger.info("=" * 70)
        self.logger.info("All models trained successfully")
        self.logger.info("=" * 70)

        # Print summary
        self.logger.info("\nModel Performance Summary:")
        for model_name, metrics in self.model_metrics.items():
            self.logger.info(
                f"  {model_name}: RMSE={metrics['rmse']:.4f}, QWK={metrics['qwk']:.4f}"
            )

        return self.model_metrics

    def get_best_model(self, metric: str = "qwk", maximize: bool = True) -> str:
        """
        Get the best model based on a metric.

        Args:
            metric: Metric name ('rmse' or 'qwk')
            maximize: Whether to maximize (True) or minimize (False) the metric

        Returns:
            Name of the best model
        """
        if not self.model_metrics:
            raise ValueError("No models have been trained yet")

        best_value = float("-inf") if maximize else float("inf")
        best_model = None

        for model_name, metrics in self.model_metrics.items():
            value = metrics[metric]
            if maximize and value > best_value:
                best_value = value
                best_model = model_name
            elif not maximize and value < best_value:
                best_value = value
                best_model = model_name

        self.logger.info(f"Best model ({metric}): {best_model} with {metric}={best_value:.4f}")

        return best_model

    def register_best_model(self, best_model_name: str):
        """
        Registra el mejor modelo entrenado en el MLflow Model Registry.

        Args:
            best_model_name: Nombre del mejor modelo (ej. 'LightGBM', 'XGBoost', 'CatBoost')
        """
        from mlflow.tracking import MlflowClient

        client = MlflowClient(tracking_uri=f"file:{self.mlflow_dir}")

        # Obtener el experimento actual
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        if not experiment:
            raise ValueError(f"El experimento '{self.experiment_name}' no existe en MLflow.")

        # Buscar el último run del modelo con ese nombre
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string=f"tags.mlflow.runName = '{best_model_name}'",
            order_by=["start_time DESC"],
            max_results=1,
        )

        if not runs:
            raise ValueError(f"No se encontró ningún run para el modelo '{best_model_name}'.")

        best_run = runs[0]
        run_id = best_run.info.run_id
        model_uri = f"runs:/{run_id}/model"

        # Nombre en el registry (puede ser igual al modelo)
        registered_model_name = f"{self.experiment_name.replace(' ', '_')}_{best_model_name}"

        self.logger.info(f"📦 Registrando modelo '{best_model_name}' en MLflow Registry...")

        # Registrar el modelo
        result = mlflow.register_model(model_uri=model_uri, name=registered_model_name)

        self.logger.info(
            f"✅ Modelo '{best_model_name}' registrado en MLflow Registry como '{registered_model_name}' "
            f"(versión: {result.version})"
        )

        # Etiquetar versión como candidata para producción
        client.set_model_version_tag(
            name=registered_model_name,
            version=result.version,
            key="stage",
            value="candidate-for-production",
        )

        return result

    def run_pipeline(
        self,
        target_column: str = "Performance",
        test_size: float = 0.2,
        random_state: int = 13,
        train_all: bool = True,
        model: Optional[str] = None,
        hyperparameters: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> Dict[str, Dict[str, float]]:
        """
        Execute the complete model training pipeline.

        Args:
            target_column: Name of the target column
            test_size: Proportion of data for testing
            random_state: Random seed for reproducibility
            train_all: Whether to train all models

        Returns:
            Dictionary mapping model names to their metrics
        """
        self.logger.info("=" * 70)
        self.logger.info("Starting model training pipeline")
        self.logger.info("=" * 70)

        # Load data
        self.load_data(target_column=target_column)

        # Split data
        self.split_data(
            target_column=target_column,
            test_size=test_size,
            random_state=random_state,
        )

        # Train models
        if train_all:
            metrics = self.train_all_models(hyperparameters=hyperparameters)
        else:
            if model == "lightgbm":
                self.train_lightgbm(
                    params=hyperparameters.get("lightgbm") if hyperparameters else None
                )
            elif model == "xgboost":
                self.train_xgboost(
                    params=hyperparameters.get("xgboost") if hyperparameters else None
                )
            elif model == "catboost":
                self.train_catboost(
                    params=hyperparameters.get("catboost") if hyperparameters else None
                )
            else:
                self.logger.error(f"Modelo NO soportado: {model}")
                raise ValueError(f"Modelo NO soportado: {model}")
            metrics = self.model_metrics

        self.logger.info("=" * 70)
        self.logger.info("Model training pipeline completed")
        self.logger.info("=" * 70)

        return metrics


def main():
    """Main function to run model training pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Train models for student performance prediction")
    parser.add_argument(
        "--input",
        type=str,
        default="data/processed/student_performance_features.csv",
        help="Path to features CSV file",
    )
    parser.add_argument(
        "--mlflow-dir",
        type=str,
        default="data/mlflow",
        help="Directory for MLflow tracking",
    )
    parser.add_argument(
        "--experiment-name",
        type=str,
        default="mlflow-student-performance-experiment",
        help="Name of MLflow experiment",
    )
    parser.add_argument(
        "--target",
        type=str,
        default="Performance",
        help="Name of target column",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Proportion of data for testing (default: 0.2)",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=13,
        help="Random seed for reproducibility (default: 13)",
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=["lightgbm", "xgboost", "catboost", "all"],
        default="all",
        help="Which model(s) to train (default: all)",
    )

    args = parser.parse_args()

    trainer = ModelTrainer(
        input_path=args.input,
        mlflow_dir=args.mlflow_dir,
        experiment_name=args.experiment_name,
    )

    trainer.run_pipeline(
        target_column=args.target,
        test_size=args.test_size,
        random_state=args.random_state,
        hyperparameters=None,  # Could be extended to load hyperparameters from a config file
        model=None if args.model == "all" else args.model,
        train_all=(args.model == "all"),
    )

    best_model = trainer.get_best_model()
    print(f"\n✅ Model training completed! Best model: {best_model}")
    print(f"📂 MLflow experiments saved to: {trainer.mlflow_dir}")
    print(f"🌐 To view MLflow UI, run: mlflow ui --backend-store-uri file:{trainer.mlflow_dir}")


if __name__ == "__main__":
    main()
