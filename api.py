"""
FastAPI application for Student Performance Prediction.

This API provides endpoints for predicting student performance based on
various academic and demographic features.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import joblib
import mlflow
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import yaml


# ====================================================
# 📋 CONFIGURATION
# ====================================================

# Load config
def load_config(config_path: str = "config/training.yaml") -> dict:
    """Load YAML configuration."""
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


config = load_config()
paths = config["paths"]
model_cfg = config["model_training"]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger("api")


# ====================================================
# 🎯 PYDANTIC MODELS (Request/Response)
# ====================================================

class StudentInput(BaseModel):
    """Input schema for student performance prediction."""
    
    Caste: str = Field(..., description="Student caste category (e.g., GENERAL, OBC, SC, ST)")
    coaching: str = Field(..., description="Coaching attendance (e.g., OA, NO, WA)")
    Class_ten_education: str = Field(..., description="Class 10 education board (e.g., SEBA, CBSE)")
    medium: str = Field(..., description="Medium of instruction (e.g., ENGLISH, ASSAMESE)")
    Class_X_Percentage: str = Field(..., description="Class X percentage category (e.g., EXCELLENT, VG, GOOD, AVERAGE)")
    Class_XII_Percentage: str = Field(..., description="Class XII percentage category (e.g., EXCELLENT, VG, GOOD, AVERAGE)")
    Father_occupation: str = Field(..., description="Father's occupation")
    Mother_occupation: str = Field(..., description="Mother's occupation")

    class Config:
        json_schema_extra = {
            "example": {
                "Caste": "GENERAL",
                "coaching": "WA",
                "Class_ten_education": "SEBA",
                "medium": "ENGLISH",
                "Class_X_Percentage": "EXCELLENT",
                "Class_XII_Percentage": "VG",
                "Father_occupation": "ENGINEER",
                "Mother_occupation": "SCHOOL_TEACHER"
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for predictions."""
    
    prediction: str = Field(..., description="Predicted performance category")
    prediction_numeric: int = Field(..., description="Numeric prediction (0-3)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediction": "EXCELLENT",
                "prediction_numeric": 3
            }
        }


class HealthResponse(BaseModel):
    """Response schema for health check."""
    
    status: str
    model_loaded: bool
    preprocessors_loaded: bool


# ====================================================
# 🔧 PREPROCESSING & MODEL LOADING
# ====================================================

class ModelPredictor:
    """Handles model loading and prediction pipeline."""
    
    def __init__(self):
        self.model = None
        self.onehot_encoder = None
        self.pca_model = None
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
        self.prediction_mapping = {
            0: "AVERAGE",
            1: "GOOD",
            2: "VG",
            3: "EXCELLENT"
        }
        
        self.nominal_variables = [
            "Caste",
            "coaching",
            "Class_ten_education",
            "medium",
            "Father_occupation",
            "Mother_occupation",
        ]
        
        self.ordinal_variables = [
            "Class_X_Percentage",
            "Class_XII_Percentage",
        ]
        
    def load_artifacts(self):
        """Load all necessary artifacts (model, encoder, PCA)."""
        try:
            # Load preprocessors
            encoder_path = Path("models/encoders/onehot_encoder.pkl")
            pca_path = Path("models/preprocessors/pca_model.pkl")
            
            if encoder_path.exists():
                self.onehot_encoder = joblib.load(encoder_path)
                logger.info(f"✅ Loaded OneHot encoder from {encoder_path}")
            else:
                raise FileNotFoundError(f"Encoder not found at {encoder_path}")
            
            if pca_path.exists():
                self.pca_model = joblib.load(pca_path)
                logger.info(f"✅ Loaded PCA model from {pca_path}")
            else:
                raise FileNotFoundError(f"PCA model not found at {pca_path}")
            
            # Load MLflow model
            mlflow_dir = Path(paths["mlflow_dir"])
            mlflow.set_tracking_uri(f"file:{mlflow_dir}")
            
            # Get the latest registered model
            experiment_name = model_cfg["experiment_name"]
            
            # Try to load from MLflow Model Registry
            try:
                from mlflow.tracking import MlflowClient
                client = MlflowClient(tracking_uri=f"file:{mlflow_dir}")
                
                # List all registered models
                registered_models = client.search_registered_models()
                
                if not registered_models:
                    raise ValueError("No registered models found in MLflow")
                
                # Get the first registered model
                model_name = registered_models[0].name
                latest_version = client.get_latest_versions(model_name, stages=["None"])[0]
                
                model_uri = f"models:/{model_name}/{latest_version.version}"
                self.model = mlflow.sklearn.load_model(model_uri)
                logger.info(f"✅ Loaded model '{model_name}' version {latest_version.version} from MLflow Registry")
                
            except Exception as e:
                logger.warning(f"Could not load from MLflow Registry: {e}")
                logger.info("Trying to load from latest run...")
                
                # Fallback: Load from latest run
                experiment = mlflow.get_experiment_by_name(experiment_name)
                if not experiment:
                    raise ValueError(f"Experiment '{experiment_name}' not found")
                
                runs = mlflow.search_runs(
                    experiment_ids=[experiment.experiment_id],
                    order_by=["start_time DESC"],
                    max_results=1
                )
                
                if runs.empty:
                    raise ValueError(f"No runs found in experiment '{experiment_name}'")
                
                run_id = runs.iloc[0].run_id
                model_uri = f"runs:/{run_id}/model"
                self.model = mlflow.sklearn.load_model(model_uri)
                logger.info(f"✅ Loaded model from run {run_id}")
            
        except Exception as e:
            logger.error(f"❌ Error loading artifacts: {e}")
            raise
    
    def preprocess_input(self, input_data: StudentInput) -> np.ndarray:
        """Preprocess input data through the same pipeline as training."""
        
        # Convert to DataFrame
        df = pd.DataFrame([input_data.dict()])
        
        # Encode ordinal variables
        for col in self.ordinal_variables:
            if col in df.columns:
                df[col] = df[col].map(self.ordinal_mapping[col])
        
        # OneHot encode nominal variables
        if self.onehot_encoder and self.nominal_variables:
            nominal_encoded = self.onehot_encoder.transform(df[self.nominal_variables])
            nominal_feature_names = self.onehot_encoder.get_feature_names_out(self.nominal_variables)
            nominal_df = pd.DataFrame(
                nominal_encoded,
                columns=nominal_feature_names,
                index=df.index
            )
            
            # Drop original nominal and ordinal columns, keep only encoded features
            df = df.drop(columns=self.nominal_variables + self.ordinal_variables)
            df = pd.concat([df, nominal_df], axis=1)
        
        # Apply PCA
        if self.pca_model:
            X_pca = self.pca_model.transform(df.values)
            return X_pca
        
        return df.values
    
    def predict(self, input_data: StudentInput) -> PredictionResponse:
        """Make prediction on input data."""
        
        if self.model is None:
            raise ValueError("Model not loaded. Call load_artifacts() first.")
        
        # Preprocess
        X_processed = self.preprocess_input(input_data)
        
        # Predict
        y_pred = self.model.predict(X_processed)
        y_pred_class = int(np.rint(y_pred[0]))
        
        # Clip to valid range [0, 3]
        y_pred_class = max(0, min(3, y_pred_class))
        
        # Map to string label
        prediction_label = self.prediction_mapping[y_pred_class]
        
        return PredictionResponse(
            prediction=prediction_label,
            prediction_numeric=y_pred_class
        )


# ====================================================
# 🚀 FASTAPI APPLICATION
# ====================================================

app = FastAPI(
    title="Student Performance Prediction API",
    description="API for predicting student academic performance based on various features",
    version="1.0.0",
)

# Initialize predictor
predictor = ModelPredictor()


@app.on_event("startup")
async def startup_event():
    """Load model and preprocessors on startup."""
    logger.info("🚀 Starting API server...")
    try:
        predictor.load_artifacts()
        logger.info("✅ All artifacts loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load artifacts: {e}")
        logger.warning("⚠️ API will start but predictions will fail until artifacts are loaded")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Student Performance Prediction API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model_loaded=predictor.model is not None,
        preprocessors_loaded=(
            predictor.onehot_encoder is not None and 
            predictor.pca_model is not None
        )
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict(student: StudentInput):
    """
    Predict student performance based on input features.
    
    Returns the predicted performance category (AVERAGE, GOOD, VG, EXCELLENT).
    """
    try:
        prediction = predictor.predict(student)
        logger.info(f"Prediction made: {prediction.prediction}")
        return prediction
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# ====================================================
# 🏃 RUN SERVER
# ====================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )