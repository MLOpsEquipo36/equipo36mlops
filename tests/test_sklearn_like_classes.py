import pytest
from pathlib import Path
from src.pipeline.sklearn_like_classes import (
    DataCleaningStep,
    FeatureBuildingStep,
    ModelTrainingStep,
)

# DataFrame mínimo válido para el pipeline
VALID_DF_TEXT = """Performance,Gender,Caste,coaching,time,Class_ten_education,twelve_education,medium,Class_X_Percentage,Class_XII_Percentage,Father_occupation,Mother_occupation
Excellent,MALE,OBC,NO,ONE,SEBA,AHSEC,ENGLISH,90,85,DOCTOR,HOUSE_WIFE
Good,FEMALE,SC,WA,TWO,SEBA,CBSE,ENGLISH,80,80,TEACHER,HOUSE_WIFE
Poor,MALE,ST,OA,ONE,CBSE,CBSE,HINDI,70,75,OTHER,HOUSE_WIFE
"""

# DataCleaningStep

def test_data_cleaning_step_run_pipeline(tmp_path): 
    input_file = tmp_path / "raw.csv"
    output_file = tmp_path / "clean.csv"

    input_file.write_text(VALID_DF_TEXT)

    step = DataCleaningStep(input_path=input_file, output_path=output_file, force=True)
    result = step.fit(None)

    assert result is step
    assert output_file.exists()

def test_data_cleaning_step_transform(tmp_path):
    input_file = tmp_path / "raw.csv"
    output_file = tmp_path / "clean.csv"

    input_file.write_text(VALID_DF_TEXT)

    step = DataCleaningStep(input_path=input_file, output_path=output_file, force=True)
    step.fit(None)

    assert step.transform(None) == output_file

# FeatureBuildingStep

def test_feature_building_step_run_pipeline(tmp_path):
    input_file = tmp_path / "clean.csv"
    output_file = tmp_path / "features.csv"

    input_file.write_text(VALID_DF_TEXT)

    step = FeatureBuildingStep(
        input_path=input_file,
        output_path=output_file,
        variance_threshold=0.9,
        force=True
    )

    result = step.fit(None)
    assert result is step
    assert output_file.exists()

def test_feature_building_step_transform(tmp_path):
    input_file = tmp_path / "clean.csv"
    output_file = tmp_path / "features.csv"

    input_file.write_text(VALID_DF_TEXT)

    step = FeatureBuildingStep(
        input_path=input_file,
        output_path=output_file,
        variance_threshold=0.9,
        force=True
    )

    step.fit(None)
    assert step.transform(None) == output_file

# ModelTrainingStep

def test_model_training_step_fit(tmp_path, monkeypatch):
    # CSV válido para todo el pipeline
    input_file = tmp_path / "features.csv"
    input_file.write_text("f1,f2,Performance\n1,2,Good\n2,3,Good\n3,4,Good")

    # Mock basado en el pipeline real
    class DummyTrainer:
        def __init__(self, *args, **kwargs):
            self.mlflow_dir = tmp_path
            self.model_metrics = {"dummy": {"rmse": 1.0}}

        def run_pipeline(self, *args, **kwargs):
            return

        def get_best_model(self, metric="rmse"):
            return "dummy"

    monkeypatch.setattr(
        "src.pipeline.sklearn_like_classes.ModelTrainer", DummyTrainer
    )

    step = ModelTrainingStep(
        input_path=input_file,
        metric="rmse",
        force=True,
    )

    result = step.fit(None)
    assert result is step
    assert step.best_model == "dummy"

def test_model_training_transform():
    step = ModelTrainingStep(
        input_path="dummy.csv",
        metric="rmse",
        force=True
    )

    if hasattr(step, "transform"):
        result = step.transform()
        assert result is step
    else:
        assert True