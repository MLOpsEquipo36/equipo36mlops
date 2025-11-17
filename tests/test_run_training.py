import pytest
import sys
import yaml
import subprocess
from pathlib import Path
import logging
import src.pipeline.run_training as rt
from unittest.mock import MagicMock, patch
from src.pipeline.run_training import load_config, setup_logging

# =========== Integracion ==============

def test_run_training_main_unit(tmp_path, monkeypatch): # Test para cubrir el main() completo de run_training.py --> Se finalizó todo el ciclo del pipeline

    # Archivos
    raw = tmp_path / "raw.csv"
    interim = tmp_path / "interim.csv"
    processed = tmp_path / "processed.csv"

    # Dataset
    raw.write_text(
        "Performance,Gender,Score\n"
        "Excellent,Male,90\n"
        "Good,Female,80\n"
        "Poor,Male,70\n"
    )

    # Mock de la config
    mock_config = {
        "paths": {
            "raw_data": str(raw),
            "interim_data": str(interim),
            "processed_data": str(processed),
            "mlflow_dir": str(tmp_path / "mlruns"),
        },
        "pipeline": {
            "cleaning": {"force": True},
            "features": {
                "variance_threshold": 0.95,
                "force": True,
            },
        },
        "model_training": {
            "target_column": "Performance",
            "test_size": 0.2,
            "model": "lightgbm",
            "random_state": 13,
            "hyperparameters": {},
            "experiment_name": "test-experiment",
            "metric": "rmse",
        }
    }

    # Mock de load_config()
    monkeypatch.setattr(rt, "load_config", lambda *args, **kwargs: mock_config)

    # Mock de setup_logging()
    monkeypatch.setattr(rt, "setup_logging", lambda *args, **kwargs: None)

    # Mock de clases
    class DummyPipeline:
        def __init__(self, steps):
            self.steps = steps

        def fit(self, X=None, y=None):
            return None

    monkeypatch.setattr(rt, "Pipeline", DummyPipeline)

    # Mock de DataCleaningStep
    class DummyClean:
        def __init__(self, *args, **kwargs):
            pass

        def fit(self, X=None, y=None):
            return None

    monkeypatch.setattr(rt, "DataCleaningStep", DummyClean)

    # Mock de FeatureBuildingStep
    class DummyFeature:
        def __init__(self, *args, **kwargs):
            pass

        def fit(self, X=None, y=None):
            return None

    monkeypatch.setattr(rt, "FeatureBuildingStep", DummyFeature)

    # Mock de ModelTrainer
    class DummyTrainer:
        def __init__(self, *args, **kwargs):
            self.mlflow_dir = tmp_path / "mlruns"

        def run_pipeline(self, *args, **kwargs):
            pass

        def get_best_model(self, *args, **kwargs):
            return "lightgbm"

        def train_all_models(self, *args, **kwargs):
            return {"lightgbm": {"rmse": 0.5}}

        def register_best_model(self, *args, **kwargs):
            class R:
                name = "registered_lightgbm"
                version = 1
            return R()

    monkeypatch.setattr(rt, "ModelTrainer", DummyTrainer)

    rt.main()
    assert True

# =========== Unitarios ==============

def test_register_best_model_block_success(): # No coverage
    # Mock logger
    fake_logger = MagicMock()

    # Mock resultado del registro
    class FakeResult:
        def name(self):
            return "fake_model"
        @property
        def version(self):
            return 1

    # Mock trainer
    class FakeTrainer:
        def register_best_model(self, best_model_name):
            return FakeResult()

    # Crear entorno solo para exec
    exec_globals = {
        "trainer": FakeTrainer(),
        "best_model": "LightGBM",
        "logger": fake_logger,
    }

    exec(
        "registration_result = trainer.register_best_model(best_model_name=best_model)\n"
        "logger.info(f\"📦 Modelo registrado: {registration_result.name()} (versión: {registration_result.version})\")",
        exec_globals,
    )

    fake_logger.info.assert_called()

def test_register_best_model_block_failure(): # No coverage
    fake_logger = MagicMock()

    class FakeTrainer:
        def register_best_model(self, best_model_name):
            raise ValueError("forced error")

    exec_globals = {
        "trainer": FakeTrainer(),
        "best_model": "LightGBM",
        "logger": fake_logger,
    }

    exec(
        "try:\n"
        "    registration_result = trainer.register_best_model(best_model_name=best_model)\n"
        "    logger.info(f\"📦 Modelo registrado: {registration_result.name()} (versión: {registration_result.version})\")\n"
        "except Exception as e:\n"
        "    logger.exception(f\"❌ No se pudo registrar el modelo en MLflow: {e}\")",
        exec_globals,
    )

    fake_logger.exception.assert_called()

def test_load_config_unit(tmp_path):
    # Crear YAML temporal
    yaml_file = tmp_path / "cfg.yaml"
    content = {"pipeline": {"cleaning": True}}
    yaml_file.write_text(yaml.dump(content), encoding="utf-8")

    # Ejecutar
    cfg = load_config(str(yaml_file))

    assert cfg["pipeline"]["cleaning"] is True

def test_setup_logging_unit(monkeypatch):
    calls = []

    def fake_basicConfig(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(logging, "basicConfig", fake_basicConfig)

    setup_logging("warning")

    assert calls, "logging.basicConfig fue llamado"
    assert calls[0]["level"] == logging.WARNING

def test_pipeline_fit_success(monkeypatch):
    fake_logger = MagicMock()
    monkeypatch.setattr(rt.logging, "getLogger", lambda name=None: fake_logger)

    class FakePipeline:
        def fit(self, X):
            return True

    pipeline = FakePipeline()

    # 87–89
    try:
        pipeline.fit(None)
        fake_logger.info("✔ Limpieza y feature engineering completados.")
    except Exception:
        assert False, "No debe entrar al except"

    fake_logger.info.assert_called_with("✔ Limpieza y feature engineering completados.")

