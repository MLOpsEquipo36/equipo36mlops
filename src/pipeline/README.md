# Vista general

En la carpeta "pipeline", podremos encontrar los scripts de python que definen la lógica de ejecución de un Pipeline de extremo a extremo para predecir el desempeño estudiantil, con etapas claras y reproducibles: limpieza de datos, ingeniería de características, entrenamiento de modelos y tracking/registro de experimentos con MLflow.

Los principales objetivos del desarrollo del pipeline son:

* Modularidad: cada etapa (limpieza, features, entrenamiento) está implementada como componentes desacoplados e independientes hasta cierto punto.

* Reproducibilidad: semillas aleatorias fijas, configuraciones centralizadas en YAML y logging consistente.

* Observabilidad: métricas, parámetros y artefactos son enviados a MLflow para auditoría y comparación de experimentos.

* Practicidad: soporta entrenar múltiples modelos (LightGBM, XGBoost, CatBoost), evaluación con métricas relevantes (RMSE, QWK) y registro automático del mejor modelo en el MLflow Model Registry.

# Archivos y carpetas clave

* config/training.yaml — Archivo YAML que centraliza rutas, parámetros de entrenamiento, y toggles del pipeline.

* src/pipeline/run_training.py — Script que ejecuta: limpieza → creación de features → entrenamiento → registro.

* src/models/train_model.py — Implementa ModelTrainer que:
    * Carga datos procesados,
    * Separa train/test,
    * Entrena LightGBM, XGBoost y CatBoost (cada uno con su método),
    * Calcula RMSE y QWK,
    * Loggea parámetros, métricas y modelos en MLflow,
    * Registra el mejor modelo en el Model Registry.

* data/mlflow/ — Store local de MLflow (puede cambiarse por un backend remoto).

# Configuración

Toda la configuración del pipeline se centraliza en un único archivo YAML ubicado en:

```bash
config/training.yaml
```
Esto permite modificar rutas, parámetros del modelo, métricas y opciones de ejecución sin tocar el código fuente.

A continuación se muestra un ejemplo de configuración típica:

```yaml
paths:
  raw_data: data/raw/student_performance.csv
  interim_data: data/interim/student_performance.csv
  processed_data: data/processed/student_performance_features.csv
  mlflow_dir: data/mlflow

pipeline:
  cleaning:
    force: false                   # Si es true, fuerza la limpieza aunque ya exista un archivo limpio
  features:
    variance_threshold: 0.01        # Umbral para eliminar variables con baja varianza
    force: false
  training:
    metric: qwk                     # Métrica principal (qwk o rmse)

model_training:
  target_column: Performance         # Columna objetivo a predecir
  test_size: 0.2                     # Proporción del conjunto de test
  random_state: 13                   # Semilla fija para reproducibilidad
  model: all                         # Opciones: 'lightgbm', 'xgboost', 'catboost' o 'all'
  experiment_name: mlflow-student-performance-experiment
  hyperparameters: {}                # Parámetros del modelo (vacío usa valores por defecto)
```

💡 Notas:

* Los directorios indicados en paths se crean automáticamente si no existen.

* Puedes cambiar el modelo a entrenar con model: "lightgbm" o cualquier otro soportado.

* force: true permite regenerar datos o features aunque los archivos ya existan.

* Todas las métricas, artefactos y parámetros se registran automáticamente en MLflow.

# Uso

El pipeline está diseñado para ejecutarse con un solo comando, ejecutando todas las etapas: limpieza → features → entrenamiento → registro del modelo.

```bash
    python -m src.pipeline.run_training
```

Durante la ejecución verás mensajes informativos en consola y en logs (si están habilitados), por ejemplo:

```bash
2025-11-02 11:01:18 - INFO - pipeline - 🚀 Iniciando pipeline de entrenamiento completo...
2025-11-02 11:01:18 - INFO - feature_engineering - 🟡 Features ya existen, se omite...
2025-11-02 11:01:19 - INFO - pipeline - Training and evaluating model: LightGBM
2025-11-02 11:01:21 - INFO - pipeline - Metrics - RMSE: 0.8376, QWK: 0.5564
2025-11-02 11:01:40 - INFO - pipeline - 🏆 Mejor modelo: LightGBM
2025-11-02 11:01:41 - INFO - pipeline - ✅ Pipeline de entrenamiento finalizado con éxito.
```

## Visualizar experimentos en MLflow

Para inspeccionar tus corridas de entrenamiento y comparar modelos visualmente:

```bash
mlflow ui --backend-store-uri file:data/mlflow
```

Luego abre en tu navegador:
👉 http://localhost:5000

Desde la interfaz de MLflow podrás:

* Visualizar métricas, parámetros y artefactos.

* Descargar modelos entrenados.

* Promover versiones al MLflow Model Registry.