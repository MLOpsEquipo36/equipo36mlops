# 📊 Metrics Monitoring — Proyecto MLOps (Rol SRE)

> **Propósito:** asegurar **reproducibilidad**, **disponibilidad de artefactos** y **calidad operacional** del pipeline de ML usando **DVC** + **MLflow**.

---

## 1. KPIs del proyecto

**Métricas base (llenar en cada ejecución):**
- **RMSE (Root Mean Square Error):** precisión del modelo de regresión.
- **QWK (Quadratic Weighted Kappa):** concordancia en clasificación ordinal.
- **Training Time (s):** segundos totales de entrenamiento por *run*.
- **Data/Concept Drift (%):** distancia entre distribuciones (por ejemplo, PSI/KL/JS).

**Tabla de resultados recientes** (agrega filas por cada *run* aprobado como baseline o candidato):
| Fecha | Run Name | Run ID | RMSE | QWK | Tiempo (s) | Drift (%) | Params hash |
|------|----------|--------|------|-----|------------|-----------|-------------|
| 2025-10-29 | ejemplo_run | 000000 | 0.123 | 0.87 | 45.3 | 1.2 | a1b2c3 |

**Notas:**  
- RMSE aplica a regresión; reemplazar por la métrica correspondiente si el problema es clasificación (Accuracy/AUC/F1).  
- QWK aplica a problemas de evaluación ordinal (opcional si no aplica).

---

## 2. Integridad de versiones — DVC + MLflow

**Regla:** todo **tag** de versión (Git/DVC) debe tener un **run** asociado en MLflow con las mismas entradas/artefactos.

**Checklist por versión:**
- [ ] Existe **tag** en Git (ej.: `v1.0.0`).
- [ ] `dvc.lock` y `dvc.yaml` versionados con el tag.
- [ ] `dvc push` ejecutado (remoto de datos actualizado).
- [ ] Existe **MLflow run** con `mlflow.set_tag("version", "<tag>")`.
- [ ] Métricas y artefactos (modelo, métricas.json) disponibles en MLflow.

**Tabla de correspondencia:**
| DVC/Git Tag | MLflow Run ID | Experimento | Estado |
|-------------|----------------|-------------|--------|
| v1.0.0 | 4e7f2ab | Default | ✅ |
| v1.0.1 | c5d9b8e | Default | ✅ |
| v1.0.2 | — | — | ❌ Falta run asociado |

**Comandos de apoyo:**

```bash
# Tags y estado DVC
git tag
dvc status
dvc metrics show

# MLflow UI local
mlflow ui  # abre http://localhost:5000
```

**Sugerencia de tagging desde el código de entrenamiento:**

```python
import mlflow

mlflow.set_experiment("default")
with mlflow.start_run(run_name="train_xgboost") as run:
    mlflow.set_tag("version", "v1.0.0")
    mlflow.set_tag("stage", "training")
    # Log params y metrics
    # mlflow.log_param("max_depth", max_depth)
    # mlflow.log_metric("rmse", rmse)
```

---

## 3. Reproducibilidad de extremo a extremo

**Objetivo:** `dvc repro` en entorno limpio produce **artefactos idénticos** (mismos hashes DVC).

**Procedimiento recomendado:**

```bash
# 1) Limpieza de workspace (cuidado: eliminará artefactos no versionados)
git clean -fdx

# 2) Traer dependencias y datos
dvc pull

# 3) Reproducir el pipeline
dvc repro

# 4) Verificar si hubo cambios (ideal: no cambios)
dvc status
```

**Registro en logs** (adjunta salida/estado):  

```bash
echo "$(date '+%Y-%m-%d %H:%M:%S') - dvc repro successful with identical outputs." >> logs/reproducibility.log
```

> Si `dvc status` reporta cambios inesperados, investigar: semillas aleatorias, versiones de librerías, dependencia no declarada, rutas relativas/absolutas, uso de `time()` o `now()` en el pipeline, etc.

---

## 4. Plan de monitoreo continuo y alertas

**Métricas a seguir en cada iteración:**
- **Calidad del modelo:** RMSE/QWK/Accuracy/AUC (según problema).
- **Eficiencia:** `train_time_s`, memoria pico, uso de CPU/GPU (si aplica).
- **Drift:** PSI/KL/JS u otras; *trigger* de reentrenamiento si supera umbral.
- **Disponibilidad de artefactos:** existencia de `models/`, `metrics.json`, `figs/`, *run* en MLflow y *tag* DVC.

**Periodicidad sugerida:**
- `dvc repro` y verificación de hashes: **semanal**.
- Revisión de métricas en MLflow y comparación con baseline: **por *commit* significativo**.

**Umbrales de alerta (ejemplo):**
- **RMSE** > 1.10 × RMSE_baseline → ⚠️ revisar datos/feature store.
- **QWK** < 0.70 → ⚠️ degradación de consistencia.
- **Drift** > 5% → ⚠️ evaluar *retraining*.
- **train_time_s** > 1.25 × baseline → ⚠️ revisar recursos/hiperparámetros.

**Canales de alerta (propuesta):**
- Webhooks de MLflow a Slack/Teams.
- Exportador a **Prometheus** + tableros **Grafana**.
- Jobs programados (Cron/GitHub Actions) que ejecuten validaciones y envíen estado.

---

## 5. Evidencia para entrega (PDF)

**Checklist de capturas:**
- [ ] Pantallas de **MLflow** con métricas y artefactos por *run*.
- [ ] Terminal con `dvc repro` exitoso.
- [ ] Tabla de integridad DVC/MLflow (sección 2 de este documento).
- [ ] `dvc status` sin cambios tras repro (opcional captura).

**Ruta sugerida:**
```
reports/imgs/mlflow_runs.png
reports/imgs/dvc_repro_ok.png
reports/imgs/dvc_status_clean.png
```
**Exportar a PDF (cuando tengas Pandoc instalado):**
```bash
pandoc reports/metrics_monitoring.md -o reports/metrics_monitoring.pdf
```

---

## 6. Apéndice A — Snippets para instrumentación

**Logging de métricas en MLflow (ejemplo):**
```python
import time, mlflow

start = time.time()
# ... entrena ...
train_time = time.time() - start

mlflow.log_metric("rmse", float(rmse))
mlflow.log_metric("qwk", float(qwk))
mlflow.log_metric("train_time_s", float(train_time))
mlflow.log_metric("data_drift_pct", float(drift_pct))
```

**Serialización de métricas a JSON (para DVC):**
```python
import json, pathlib

metrics = {
    "rmse": float(rmse),
    "qwk": float(qwk),
    "train_time_s": float(train_time),
    "data_drift_pct": float(drift_pct)
}
pathlib.Path("reports").mkdir(parents=True, exist_ok=True)
with open("reports/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
```

> Añade `reports/metrics.json` a `dvc.yaml` como **metrics** para que `dvc metrics show` lo recoja.

---

## 7. Apéndice B — Declaración de *metrics* y *plots* en DVC (ejemplo)

**`dvc.yaml` (fragmento):**
```yaml
stages:
  train:
    cmd: python src/train.py
    deps:
      - src/train.py
      - data/processed/train.parquet
      - params.yaml
    outs:
      - models/model.pkl
    metrics:
      - reports/metrics.json:
          cache: false
    plots:
      - reports/plots/roc.json:
          cache: false
```

**Visualizar métricas con DVC:**
```bash
dvc metrics show
dvc metrics diff HEAD~1
```

---

## 8. Apéndice C — Recomendaciones de *seeds* y entornos

- Fijar *seeds* en NumPy/PyTorch/TF/xgboost y cualquier fuente pseudoaleatoria.
- Capturar versiones exactas (`pip freeze > requirements.lock.txt`).
- Evitar dependencias no declaradas en `dvc.yaml` (lecturas de rutas externas, *env vars*).
- Controlar *timezone* y funciones no deterministas (uso de `now()` sólo si es insumo explícito).
- Empaquetar entrenamiento en contenedor (Docker) para reducir *drift* de entorno.

---

**Responsable del documento:** SRE — Repositorio *<NOMBRE_DEL_PROYECTO>*  
**Última actualización:** 2025-10-29 23:58:09
