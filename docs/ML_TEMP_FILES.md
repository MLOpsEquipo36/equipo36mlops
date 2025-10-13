# 🗂️ Manejo de Archivos Temporales en ML

## 📋 Resumen de Directorios Temporales

| Directorio | Generado por | ¿Qué contiene? | ¿Dónde debe estar? | Solución |
|------------|--------------|----------------|-------------------|----------|
| **`catboost_info/`** | CatBoost | Logs de entrenamiento | ❌ No debe existir | `.gitignore` + config |
| **`mlruns/`** | MLflow (default) | Experimentos | ✅ `data/mlflow/` | `.gitignore` + config correcto |
| **`.ipynb_checkpoints/`** | Jupyter | Checkpoints | ❌ No debe estar en repo | `.gitignore` |
| **`__pycache__/`** | Python | Bytecode compilado | ❌ No debe estar en repo | `.gitignore` |

---

## 1. 📁 `catboost_info/`

### ¿Qué es?

Directorio creado automáticamente por **CatBoost** durante el entrenamiento para guardar:
- `catboost_training.json` - Configuración del entrenamiento
- `learn_error.tsv` - Errores por iteración
- `time_left.tsv` - Tiempo estimado restante
- `learn/` - Eventos de TensorBoard

### ¿Por qué es un problema?

- 🚨 Se regenera en **cada ejecución**
- 🚨 Genera **conflictos** en Git si varios miembros entrenan
- 🚨 Ocupa espacio innecesario (~60KB+ por ejecución)
- 🚨 **NO aporta valor** para reproducibilidad (MLflow ya guarda métricas)

### ✅ Solución

#### Opción 1: Desactivar completamente (RECOMENDADO)

```python
from catboost import CatBoostRegressor

params_cat = {
    'iterations': 300,
    'learning_rate': 0.05,
    'depth': 6,
    'loss_function': 'RMSE',
    'random_seed': 42,
    'verbose': 0,
    'train_dir': None  # ✅ Esto evita crear catboost_info/
}

model = CatBoostRegressor(**params_cat)
```

#### Opción 2: Redirigir a un directorio temporal

```python
import tempfile

params_cat = {
    'iterations': 300,
    'learning_rate': 0.05,
    'depth': 6,
    'train_dir': tempfile.mkdtemp()  # Se crea en /tmp/ y se borra automáticamente
}

model = CatBoostRegressor(**params_cat)
```

#### Opción 3: Solo agregar a `.gitignore`

```gitignore
# En .gitignore
catboost_info/
```

**Desventaja**: El directorio seguirá creándose, solo no se subirá a Git.

---

## 2. 🔬 `mlruns/`

### ¿Qué es?

Directorio creado por **MLflow** para almacenar experimentos. Contiene:
- Parámetros de modelos
- Métricas registradas
- Artefactos (modelos guardados)
- Metadata de runs

### ¿Por qué puede aparecer en lugares incorrectos?

MLflow crea `mlruns/` en el **directorio de trabajo actual** si no configuras `tracking_uri` **antes** de cualquier operación de MLflow.

### ✅ Solución

#### En tu Notebook 3

**❌ Incorrecto** (crea `mlruns/` en `notebooks/`):

```python
import mlflow

# Primer uso sin configurar tracking_uri
mlflow.start_run()  # ❌ Crea notebooks/mlruns/
```

**✅ Correcto** (usa `data/mlflow/`):

```python
import mlflow

# PRIMERO configurar tracking_uri
mlflow.set_tracking_uri("file:../data/mlflow")

# LUEGO usar MLflow
mlflow.start_run()  # ✅ Usa data/mlflow/
```

#### Estructura Correcta del Notebook 3

```python
import mlflow
import os

# === Configuración MLflow (PRIMERA CELDA) ===
MLFLOW_TRACKING_DIR = "../data/mlflow"
mlflow.set_tracking_uri(f"file:{MLFLOW_TRACKING_DIR}")

print(f"✅ MLflow configurado: {MLFLOW_TRACKING_DIR}")

# Ahora puedes usar MLflow normalmente
experiment_name = "student-performance-experiment"
mlflow.set_experiment(experiment_name)
```

#### Limpiar directorios duplicados

```bash
# Si ya tienes notebooks/mlruns/, elimínalo
rm -rf notebooks/mlruns/

# Verifica que data/mlflow/ exista
ls -la data/mlflow/

# Agregar a .gitignore para prevenir
echo "mlruns/" >> .gitignore
```

---

## 3. 📓 `.ipynb_checkpoints/`

### ¿Qué es?

Jupyter Notebook crea checkpoints automáticos para recuperar trabajo en caso de crash.

### ✅ Solución

```gitignore
# En .gitignore
.ipynb_checkpoints/
```

**Nota**: Ya está en el `.gitignore` estándar de Python, pero verifica que esté presente.

---

## 4. 🐍 `__pycache__/`

### ¿Qué es?

Python compila módulos a bytecode (`.pyc`) para cargarlos más rápido.

### ✅ Solución

```gitignore
# En .gitignore
__pycache__/
*.py[cod]
*$py.class
```

---

## 📝 Configuración Completa de `.gitignore`

```gitignore
# Machine Learning temporary files and logs
catboost_info/
mlruns/
.ipynb_checkpoints/
__pycache__/

# Modelos y artefactos (manejados por DVC)
*.pkl
*.joblib
*.h5
*.bin
/models/**/*.pkl
/models/**/*.h5

# Python
*.py[cod]
*$py.class
__pycache__/
*.so

# Jupyter
.ipynb_checkpoints

# IDEs
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Environment
.env
.venv
env/
venv/
```

---

## 🔍 Verificación

### Después de configurar:

```bash
# 1. Verifica que .gitignore funcione
git status

# No deberías ver:
# - catboost_info/
# - mlruns/ (en notebooks/)
# - .ipynb_checkpoints/
# - __pycache__/

# 2. Re-ejecuta Notebook 3
jupyter notebook notebooks/3_Model_Training_and_Registering.ipynb

# 3. Verifica que NO se creen directorios temporales
ls -la notebooks/
# No debería haber catboost_info/ ni mlruns/

# 4. Verifica que MLflow use el directorio correcto
ls -la data/mlflow/
# Deberías ver los experimentos aquí
```

---

## 🚀 Flujo de Trabajo Recomendado

### Al crear un nuevo notebook de entrenamiento:

1. **Primera celda** - Configurar directorios:
   ```python
   import mlflow
   import os
   
   # Configurar MLflow
   MLFLOW_DIR = "../data/mlflow"
   mlflow.set_tracking_uri(f"file:{MLFLOW_DIR}")
   
   # Configurar CatBoost (si lo usas)
   os.environ['CATBOOST_SILENT'] = '1'  # Silenciar logs
   ```

2. **Al entrenar CatBoost**:
   ```python
   params = {
       # ... otros parámetros ...
       'train_dir': None,  # ✅ No crear catboost_info/
       'verbose': 0        # ✅ Sin logs en consola
   }
   ```

3. **Después de entrenar**:
   ```bash
   # Verificar que no se crearon directorios temporales
   ls -la notebooks/
   
   # Versionar solo data/mlflow/ con DVC
   bash add_to_dvc.sh data/mlflow models-v1.0 'Trained models'
   ```

---

## 🆘 Troubleshooting

### Problema 1: "catboost_info/ keeps being created"

**Causa**: No agregaste `train_dir=None` en los parámetros de CatBoost.

**Solución**:
```python
# Busca en tu notebook:
model = CatBoostRegressor(...)

# Asegúrate que tenga:
model = CatBoostRegressor(
    # ... otros parámetros ...
    train_dir=None
)
```

---

### Problema 2: "mlruns/ appears in multiple places"

**Causa**: Configuraste `mlflow.set_tracking_uri()` **después** de usar MLflow.

**Solución**:
```python
# ❌ MALO
import mlflow
mlflow.start_run()  # Crea mlruns/ aquí
mlflow.set_tracking_uri("file:../data/mlflow")  # Demasiado tarde

# ✅ BUENO
import mlflow
mlflow.set_tracking_uri("file:../data/mlflow")  # PRIMERO
mlflow.start_run()  # Ahora usa data/mlflow/
```

---

### Problema 3: "Git shows these directories as untracked"

**Causa**: `.gitignore` no se aplicó correctamente.

**Solución**:
```bash
# 1. Verificar que .gitignore tenga las entradas
grep -E "catboost_info|mlruns" .gitignore

# 2. Si ya los agregaste a Git por error, removerlos:
git rm -r --cached notebooks/catboost_info
git rm -r --cached notebooks/mlruns

# 3. Commit
git commit -m "chore: remove temporary ML directories"
```

---

## 📚 Recursos

- [CatBoost Documentation - train_dir parameter](https://catboost.ai/en/docs/concepts/python-reference_catboostregressor)
- [MLflow Tracking URI](https://mlflow.org/docs/latest/tracking.html#where-runs-are-recorded)
- [Git .gitignore patterns](https://git-scm.com/docs/gitignore)

---

**Última actualización**: Octubre 2025  
**Equipo 36 MLOps** | Tec de Monterrey

