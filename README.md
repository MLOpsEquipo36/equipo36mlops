# Equipo36MLOps

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Este es el proyecto dedicado a la materia MLOps por parte del Equipo 36 en la Maestria en Inteligencia Artificial Aplicada del Tec de Monterrey. Desarrollado para el trimestre sep-dic 2025.

## 🚀 Quick Start

### Configuración Inicial

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd equipo36mlops

# 2. Configurar credenciales AWS (para DVC)
bash setup_aws_credentials.sh

# 3. Descargar datos versionados
dvc pull
```

### Ejecutar el Pipeline

El proyecto consiste en 3 notebooks que deben ejecutarse en orden:

1. **`1_EDA_and_Cleaning.ipynb`** - Exploración y limpieza de datos
2. **`2_Data_Processing.ipynb`** - Feature engineering y PCA
3. **`3_Model_Training_and_Registering.ipynb`** - Entrenamiento de modelos con MLflow

Cada notebook incluye instrucciones para versionar los datos resultantes con DVC.

## 📦 Versionado de Datos con DVC

Este proyecto usa **DVC (Data Version Control)** para versionar datos y modelos, con almacenamiento remoto en **AWS S3**.

### Comandos Rápidos

```bash
# Versionar un archivo nuevo
bash add_to_dvc.sh <archivo> <tag> <descripción>

# Descargar datos versionados
dvc pull

# Subir datos versionados
dvc push
```

### Documentación

- 📚 **Guía completa**: [`docs/DVC_WORKFLOW.md`](docs/DVC_WORKFLOW.md)
- 📋 **Guía rápida notebooks**: [`notebooks/README_DVC.md`](notebooks/README_DVC.md)
- 🔧 **Referencia de comandos**: [`DVC_COMMANDS.md`](DVC_COMMANDS.md)
- 📦 **Artefactos ML (.pkl, modelos)**: [`docs/DVC_ARTIFACTS.md`](docs/DVC_ARTIFACTS.md)
- 🗂️ **Archivos temporales (catboost_info, mlruns)**: [`docs/ML_TEMP_FILES.md`](docs/ML_TEMP_FILES.md)

### Versiones de Datos

| Tag | Descripción | Archivo |
|-----|-------------|---------|
| `data-v1.0-raw` | Datos originales | `data/raw/student_entry_performance.csv` |
| `data-v1.1-cleaned` | Datos después de EDA | `data/processed/student_performance.csv` |
| `data-v1.2-features` | Features con PCA | `data/processed/student_performance_features.csv` |
| `artifacts-v1.0` | Artefactos de preprocesamiento | `models/encoders/`, `models/preprocessors/` |
| `models-v1.0-baseline` | Modelos baseline entrenados | `data/mlflow/` |

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         equipo36mlops and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── equipo36mlops   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes equipo36mlops a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

