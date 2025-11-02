import logging
import os

from sklearn.base import BaseEstimator, TransformerMixin

from src.data.clean_data import DataCleaner
from src.features.build_features import FeatureBuilder
from src.models.train_model import ModelTrainer


# ====================================================
# 1️⃣ Paso de Limpieza de Datos
# ====================================================
class DataCleaningStep(BaseEstimator, TransformerMixin):
    def __init__(self, input_path, output_path, force=False, logger=None):
        self.input_path = input_path
        self.output_path = output_path
        self.force = force
        self.logger = logger or logging.getLogger("data_cleaning")
        self.cleaner = None

    def fit(self, X=None, y=None):
        if os.path.exists(self.output_path) and not self.force:
            self.logger.info(f"🟡 Archivo limpio ya existe, se omite: {self.output_path}")
            return self

        self.logger.info(f"🧹 Ejecutando limpieza de datos...")
        self.cleaner = DataCleaner(
            input_path=self.input_path, output_path=self.output_path, logger=self.logger
        )
        self.cleaner.run_pipeline()
        self.cleaner.save_cleaned_data()
        self.logger.info(f"✅ Datos limpios guardados en: {self.output_path}")
        return self

    def transform(self, X=None):
        return self.output_path


# ====================================================
# 2️⃣ Paso de Feature Engineering
# ====================================================
class FeatureBuildingStep(BaseEstimator, TransformerMixin):
    def __init__(self, input_path, output_path, variance_threshold=0.9, force=False, logger=None):
        self.input_path = input_path
        self.output_path = output_path
        self.variance_threshold = variance_threshold
        self.force = force
        self.logger = logger or logging.getLogger("feature_engineering")
        self.builder = None

    def fit(self, X=None, y=None):
        if os.path.exists(self.output_path) and not self.force:
            self.logger.info(f"🟡 Features ya existen, se omite: {self.output_path}")
            return self

        self.logger.info(f"⚙️ Ejecutando feature engineering...")
        self.builder = FeatureBuilder(
            input_path=self.input_path, output_path=self.output_path, logger=self.logger
        )
        self.builder.run_pipeline(variance_threshold=self.variance_threshold)
        self.builder.save_features()
        self.builder.save_artifacts()
        self.logger.info(f"✅ Features guardadas en: {self.output_path}")
        return self

    def transform(self, X=None):
        return self.output_path


# ====================================================
# 3️⃣ Paso de Entrenamiento de Modelo
# ====================================================
class ModelTrainingStep(BaseEstimator):
    def __init__(
        self, input_path, metric: str = "qwk", hyperparameters=None, force=False, logger=None
    ):
        self.input_path = input_path
        self.metric = metric
        self.force = force
        self.logger = logger or logging.getLogger("model_training")
        self.trainer = ModelTrainer(input_path=self.input_path, logger=self.logger)
        self.best_model = None
        self.metrics = None
        self.hyperparameters = hyperparameters or {}

    def fit(self, X=None, y=None):
        self.logger.info(f"🏋️ Entrenando modelos con el PIPELINE DE SCIKIT LEARN...")
        self.metrics = self.trainer.run_pipeline()
        self.best_model = self.trainer.get_best_model(metric=self.metric)
        self.logger.info(f"✅ Mejor modelo: {self.best_model}")
        self.logger.info(f"📊 Métricas: {self.trainer.model_metrics[self.best_model]}")
        self.logger.info(f"📂 MLflow experiments saved to: {self.trainer.mlflow_dir}")
        self.logger.info(
            f"🌐 Para acceder a MLflow UI, ejecuta: mlflow ui --backend-store-uri file:{self.trainer.mlflow_dir}"
        )
        return self
