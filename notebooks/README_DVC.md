# 📦 Guía Rápida: Versionado con DVC en Notebooks

## 🚀 Inicio Rápido

### Cada vez que ejecutes un notebook:

1. **Antes de empezar**:
   ```bash
   git pull && dvc pull
   ```

2. **Después de ejecutar el notebook** (cuando se genere un archivo de salida):
   ```bash
   bash add_to_dvc.sh <archivo> <tag> <descripción>
   ```

---

## 📊 Pipeline de Notebooks

### 1️⃣ Notebook 1: `1_EDA_and_Cleaning.ipynb`

**Lee**: `data/raw/student_entry_performance.csv` (tag: `data-v1.0-raw`)  
**Guarda**: `data/processed/student_performance.csv`

**Al terminar, ejecuta**:
```bash
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned 'Dataset after EDA cleaning'
```

---

### 2️⃣ Notebook 2: `2_Data_Processing.ipynb`

**Lee**: `data/processed/student_performance.csv` (tag: `data-v1.1-cleaned`)  
**Guarda**: `data/processed/student_performance_features.csv`

**Antes de empezar**:
```bash
# Asegúrate de tener la versión correcta
dvc pull
```

**Al terminar, ejecuta**:
```bash
bash add_to_dvc.sh data/processed/student_performance_features.csv data-v1.2-features 'Features with PCA ready for modeling'
```

---

### 3️⃣ Notebook 3: `3_Model_Training_and_Registering.ipynb`

**Lee**: `data/processed/student_performance_features.csv` (tag: `data-v1.2-features`)  
**Guarda**: `data/mlflow/` (directorio con experimentos)

**Antes de empezar**:
```bash
# Asegúrate de tener la versión correcta
dvc pull
```

**Al terminar, ejecuta**:
```bash
bash add_to_dvc.sh data/mlflow models-v1.0-baseline 'Baseline models: LightGBM, XGBoost, CatBoost'
```

---

## 🏷️ Tags del Proyecto

| Tag | Descripción | Archivo/Directorio |
|-----|-------------|-------------------|
| `data-v1.0-raw` | Datos originales | `data/raw/student_entry_performance.csv` |
| `data-v1.1-cleaned` | Datos después de EDA | `data/processed/student_performance.csv` |
| `data-v1.2-features` | Features con PCA | `data/processed/student_performance_features.csv` |
| `models-v1.0-baseline` | Modelos baseline | `data/mlflow/` |

---

## 🔄 Recuperar una versión anterior

```bash
# Ejemplo: volver a la versión de datos limpios
git checkout data-v1.1-cleaned
dvc checkout

# Ver el archivo
cat data/processed/student_performance.csv

# Volver a la última versión
git checkout main  # o tu rama actual
dvc checkout
```

---

## 🆘 Comandos de Emergencia

### "Olvidé hacer dvc pull"

```bash
dvc pull
```

### "Mi notebook está leyendo un archivo que no existe"

```bash
# Probablemente necesitas descargar los datos
dvc pull

# O cambiar a la versión correcta
git checkout <tag-correcto>
dvc checkout
```

### "Quiero ver todas las versiones disponibles"

```bash
git tag -l
```

### "No sé en qué versión estoy"

```bash
git describe --tags
```

---

## 📚 Documentación Completa

Para la guía completa con troubleshooting y mejores prácticas, consulta:

👉 [`docs/DVC_WORKFLOW.md`](../docs/DVC_WORKFLOW.md)

---

**Última actualización**: Octubre 2025  
**Equipo 36 MLOps**

