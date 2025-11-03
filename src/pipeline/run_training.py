import logging

from sklearn.pipeline import Pipeline
import yaml

from src.models.train_model import ModelTrainer
from src.pipeline.sklearn_like_classes import DataCleaningStep, FeatureBuildingStep

# ====================================================
# 🔧 UTILIDADES
# ====================================================


def load_config(config_path: str = "config/training.yaml") -> dict:
    """Carga la configuración YAML del pipeline."""
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def setup_logging(level: str = "INFO"):
    """Configura el logging global del proyecto."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ====================================================
# 🚀 PIPELINE PRINCIPAL
# ====================================================


def main():
    """
    Ejecuta el pipeline completo de entrenamiento:
      1. Limpieza de datos
      2. Ingeniería de características
      3. Entrenamiento y logging de modelos
    """

    # -----------------------------------------------
    # 1️⃣ Cargar configuración y logger
    # -----------------------------------------------
    config = load_config()
    setup_logging(config.get("logging", {}).get("level", "INFO"))
    logger = logging.getLogger("pipeline")

    logger.info("🚀 Iniciando pipeline de entrenamiento completo...")

    paths = config["paths"]
    steps = config["pipeline"]
    model_cfg = config["model_training"]

    # -----------------------------------------------
    # 2️⃣ Construir pipeline sklearn
    # -----------------------------------------------
    pipeline = Pipeline(
        [
            (
                "cleaning",
                DataCleaningStep(
                    input_path=paths["raw_data"],
                    output_path=paths["interim_data"],
                    force=steps["cleaning"]["force"],
                ),
            ),
            (
                "features",
                FeatureBuildingStep(
                    input_path=paths["interim_data"],
                    output_path=paths["processed_data"],
                    variance_threshold=steps["features"]["variance_threshold"],
                    force=steps["features"]["force"],
                ),
            ),
        ]
    )

    # -----------------------------------------------
    # 3️⃣ Ejecutar limpieza y feature engineering
    # -----------------------------------------------
    try:
        pipeline.fit(None)
        logger.info("✅ Limpieza y feature engineering completados.")
    except Exception as e:
        logger.exception(f"❌ Error en las etapas iniciales del pipeline: {e}")
        return

    # -----------------------------------------------
    # 4️⃣ Entrenamiento de modelos (ModelTrainer)
    # -----------------------------------------------
    try:
        trainer = ModelTrainer(
            input_path=paths["processed_data"],
            mlflow_dir=paths["mlflow_dir"],
            experiment_name=model_cfg["experiment_name"],
            logger=logger,
        )

        trainer.run_pipeline(
            target_column=model_cfg["target_column"],
            test_size=model_cfg["test_size"],
            random_state=model_cfg["random_state"],
            hyperparameters=model_cfg.get("hyperparameters"),
            train_all=(model_cfg["model"] == "all"),
            model=None if model_cfg["model"] == "all" else model_cfg["model"],
        )

        best_model = trainer.get_best_model(metric=steps["training"]["metric"])
        logger.info(f"🏆 Mejor modelo: {best_model}")
        logger.info(f"📂 MLflow guardado en: {paths['mlflow_dir']}")
        _aux_model_path = str(trainer.mlflow_dir).replace("\\", "/")
        logger.info(
            f"🌐 Para visualizar los resultados en el navegador ejecuta: mlflow ui --backend-store-uri file:{_aux_model_path}"
        )
        # 👉 Registrar el mejor modelo en el MLflow Model Registry
        try:
            registration_result = trainer.register_best_model(best_model_name=best_model)
            logger.info(
                f"📘 Modelo registrado: {registration_result.name} (versión {registration_result.version})"
            )
        except Exception as e:
            logger.exception(f"⚠️ No se pudo registrar el modelo en MLflow: {e}")
            return
    except Exception as e:
        logger.exception(f"❌ Error durante el entrenamiento de modelos: {e}")
        return

    logger.info("✅ Pipeline de entrenamiento finalizado con éxito.")


# ====================================================
# 🏁 ENTRYPOINT
# ====================================================

if __name__ == "__main__":
    main()
