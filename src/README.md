# 📦 Módulos Refactorizados - Estructura Cookiecutter

Este directorio contiene los scripts refactorizados de los notebooks, siguiendo buenas prácticas de MLOps, principios de POO y estructura Cookiecutter.

## 📁 Estructura

```
src/
├── __init__.py
├── data/
│   ├── __init__.py
│   └── clean_data.py          # Refactorizado de 1_EDA_and_Cleaning.ipynb
├── features/
│   ├── __init__.py
│   └── build_features.py       # Refactorizado de 2_Data_Processing.ipynb
└── models/
    ├── __init__.py
    └── train_model.py          # Refactorizado de 3_Model_Training_and_Registering.ipynb
```

## 🎯 Módulos

### 1. `src/data/clean_data.py`

**Clase principal:** `DataCleaner`

Responsabilidades:
- Cargar datos raw
- Normalización de texto (mayúsculas, trim)
- Manejo de valores nulos
- Limpieza de columnas no informativas
- Guardar datos limpios

**Uso:**

```python
from src.data import DataCleaner

cleaner = DataCleaner(
    input_path="data/raw/student_entry_performance.csv",
    output_path="data/processed/student_performance.csv"
)

# Ejecutar pipeline completo
cleaner.run_pipeline()
cleaner.save_cleaned_data()

# O usar métodos individuales
cleaner.load_data()
cleaner.normalize_case()
cleaner.trim_whitespace()
# ... más operaciones
```

**Línea de comandos:**

```bash
python -m src.data.clean_data --input data/raw/student_entry_performance.csv --output data/processed/student_performance.csv
```

### 2. `src/features/build_features.py`

**Clase principal:** `FeatureBuilder`

Responsabilidades:
- Selección de features (Chi-cuadrada, Cramer's V, Spearman)
- OneHot encoding para variables nominales
- Aplicación de PCA para reducción de dimensionalidad
- Guardar encoders y preprocessors
- Guardar features procesadas

**Uso:**

```python
from src.features import FeatureBuilder

builder = FeatureBuilder(
    input_path="data/processed/student_performance.csv",
    output_path="data/processed/student_performance_features.csv",
    encoder_dir="models/encoders",
    preprocessor_dir="models/preprocessors"
)

# Ejecutar pipeline completo
builder.run_pipeline(
    feature_selection=True,
    apply_encoding=True,
    apply_pca=True,
    variance_threshold=0.95
)

builder.save_features()
builder.save_artifacts()
```

**Línea de comandos:**

```bash
python -m src.features.build_features \
    --input data/processed/student_performance.csv \
    --output data/processed/student_performance_features.csv \
    --variance-threshold 0.95
```

### 3. `src/models/train_model.py`

**Clase principal:** `ModelTrainer`

Responsabilidades:
- Cargar features procesadas
- División train/test estratificada
- Entrenamiento de modelos (LightGBM, XGBoost, CatBoost)
- Evaluación y logging en MLflow
- Comparación de modelos

**Uso:**

```python
from src.models import ModelTrainer

trainer = ModelTrainer(
    input_path="data/processed/student_performance_features.csv",
    mlflow_dir="data/mlflow",
    experiment_name="mlflow-student-performance-experiment"
)

# Ejecutar pipeline completo
trainer.run_pipeline(
    target_column="Performance",
    test_size=0.2,
    random_state=13,
    train_all=True
)

# O entrenar modelos individuales
trainer.load_data()
trainer.split_data()
trainer.train_lightgbm()
trainer.train_xgboost()
trainer.train_catboost()

# Obtener el mejor modelo
best_model = trainer.get_best_model(metric="qwk")
```

**Línea de comandos:**

```bash
python -m src.models.train_model \
    --input data/processed/student_performance_features.csv \
    --model all \
    --target Performance
```

## 🔄 Pipeline Completo

Para ejecutar el pipeline completo desde datos raw hasta modelos entrenados:

```bash
# 1. Limpiar datos
python -m src.data.clean_data \
    --input data/raw/student_entry_performance.csv \
    --output data/processed/student_performance.csv

# 2. Construir features
python -m src.features.build_features \
    --input data/processed/student_performance.csv \
    --output data/processed/student_performance_features.csv

# 3. Entrenar modelos
python -m src.models.train_model \
    --input data/processed/student_performance_features.csv \
    --model all
```

## 🏗️ Principios de Diseño

### Programación Orientada a Objetos (POO)

- **Encapsulación**: Cada clase encapsula su propia lógica y estado
- **Responsabilidad única**: Cada clase tiene una responsabilidad bien definida
- **Reutilización**: Métodos públicos permiten flexibilidad en el uso
- **Extensibilidad**: Fácil de extender con nuevos métodos o funcionalidades

### Modularidad

- Cada módulo es independiente y puede ejecutarse por separado
- Separación clara de concerns (datos, features, modelos)
- Fácil mantenimiento y testing

### Buenas Prácticas MLOps

- **Logging estructurado**: Todas las operaciones están loggeadas
- **Reproducibilidad**: Parámetros configurables y random seeds
- **Versionado**: Compatible con DVC y MLflow
- **Pipeline automatizado**: Métodos `run_pipeline()` para ejecución completa

## 📝 Ejemplo de Uso Avanzado

```python
import logging
from src.data import DataCleaner
from src.features import FeatureBuilder
from src.models import ModelTrainer

# Configurar logging
logging.basicConfig(level=logging.INFO)

# 1. Limpieza de datos
cleaner = DataCleaner(
    input_path="data/raw/student_entry_performance.csv",
    output_path="data/processed/student_performance.csv",
    logger=logging.getLogger("data_cleaning")
)
cleaner.run_pipeline()
cleaner.save_cleaned_data()

# 2. Feature engineering
builder = FeatureBuilder(
    input_path="data/processed/student_performance.csv",
    output_path="data/processed/student_performance_features.csv",
    logger=logging.getLogger("feature_engineering")
)
builder.run_pipeline(variance_threshold=0.90)
builder.save_features()
builder.save_artifacts()

# 3. Entrenamiento
trainer = ModelTrainer(
    input_path="data/processed/student_performance_features.csv",
    logger=logging.getLogger("model_training")
)
metrics = trainer.run_pipeline()

# Comparar modelos
best_model = trainer.get_best_model(metric="qwk")
print(f"Mejor modelo: {best_model}")
print(f"Métricas: {trainer.model_metrics[best_model]}")
```

## ✅ Ventajas de la Refactorización

1. **Mantenibilidad**: Código organizado y fácil de mantener
2. **Reutilización**: Componentes reutilizables en otros proyectos
3. **Testing**: Estructura que facilita unit testing
4. **Colaboración**: Código más legible para el equipo
5. **Escalabilidad**: Fácil agregar nuevas funcionalidades
6. **Producción**: Listo para integrar en pipelines de CI/CD

## 🔧 Dependencias

Los scripts requieren las siguientes dependencias (deben estar en `pyproject.toml`):

- pandas
- numpy
- scikit-learn
- scipy
- lightgbm
- xgboost
- catboost
- mlflow
- joblib

Asegúrate de instalar todas las dependencias antes de ejecutar los scripts.

