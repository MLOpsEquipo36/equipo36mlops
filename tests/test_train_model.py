import sys
from pathlib import Path
import pandas as pd
from unittest.mock import MagicMock, patch
from src.models.train_model import ModelTrainer
import src.models.train_model as tm

# =========== Integracion ==============

def test_train_model_main_unit(tmp_path, monkeypatch):

    # 1) Crear CSV con CLASES BALANCEADAS (mínimo 2 muestras por clase)
    input_file = tmp_path / "features.csv"

    df = pd.DataFrame({
        "feature1":  [1,1,2,2,3,3],
        "feature2":  [4,4,3,3,2,2],
        "Performance": [1,1,2,2,3,3],   # cada clase tiene 2 muestras
    })

    df.to_csv(input_file, index=False)

    mlflow_dir = tmp_path / "mlflow"

    # 2) Simular argumentos CLI
    monkeypatch.setattr(sys, "argv", [
        "train_model.py",
        "--input", str(input_file),
        "--mlflow-dir", str(mlflow_dir),
        "--experiment-name", "test-exp",
        "--target", "Performance",
        "--test-size", "0.5",          # <-- FIX: asegura >= 3 muestras para test
        "--random-state", "13",
        "--model", "lightgbm"
    ])

    # 3) Ejecutar main()
    tm.main()

    # 4) Validaciones
    assert mlflow_dir.exists()
    assert any(mlflow_dir.rglob("*"))

# =========== Unitarios ==============

def test_train_all_models_unit():
    # === Crear instancia ===
    trainer = ModelTrainer(
        input_path="dummy.csv",
        mlflow_dir="dummy_mlflow",
        experiment_name="test_experiment"
    )

    # Inicializar métricas
    trainer.model_metrics = {}

    # === Mockear funciones internas simulando su comportamiento real ===
    
    def fake_lightgbm(params=None):
        trainer.model_metrics["lightgbm"] = {"rmse": 0.5, "qwk": 0.7}
        return 0.5, 0.7

    def fake_xgboost(params=None):
        trainer.model_metrics["xgboost"] = {"rmse": 0.6, "qwk": 0.65}
        return 0.6, 0.65

    def fake_catboost(params=None):
        trainer.model_metrics["catboost"] = {"rmse": 0.55, "qwk": 0.68}
        return 0.55, 0.68

    trainer.train_lightgbm = MagicMock(side_effect=fake_lightgbm)
    trainer.train_xgboost = MagicMock(side_effect=fake_xgboost)
    trainer.train_catboost = MagicMock(side_effect=fake_catboost)

    # === Ejecutar función ===
    metrics = trainer.train_all_models(hyperparameters=None)

    # === Verificaciones ===
    assert isinstance(metrics, dict)

    # Las métricas deben existir
    assert "lightgbm" in trainer.model_metrics
    assert "xgboost" in trainer.model_metrics
    assert "catboost" in trainer.model_metrics

    # Verificar contenido
    for model in trainer.model_metrics.values():
        assert "rmse" in model
        assert "qwk" in model

    # Verificar llamados
    trainer.train_lightgbm.assert_called_once()
    trainer.train_xgboost.assert_called_once()
    trainer.train_catboost.assert_called_once()

def test_register_best_model_unit():
    trainer = ModelTrainer(
        input_path="dummy.csv",
        mlflow_dir="dummy_mlflow",
        experiment_name="mlflow-student-performance-experiment"
    )

    with patch("src.models.train_model.mlflow") as mock_mlflow, \
         patch("mlflow.tracking.MlflowClient") as MockClient:   # ← SOLUCIÓN

        # ==== Mock para get_experiment_by_name ====
        mock_experiment = MagicMock()
        mock_experiment.experiment_id = "123"
        mock_mlflow.get_experiment_by_name.return_value = mock_experiment

        # ==== Mock de MlflowClient ====
        mock_client = MockClient.return_value

        mock_run = MagicMock()
        mock_run.info.run_id = "RUN123"
        mock_client.search_runs.return_value = [mock_run]

        mock_registered = MagicMock()
        mock_registered.name = "mlflow-student-performance-experiment_LightGBM"
        mock_registered.version = 1

        mock_mlflow.register_model.return_value = mock_registered

        result = trainer.register_best_model("LightGBM")

        assert result.version == 1
        assert "LightGBM" in result.name