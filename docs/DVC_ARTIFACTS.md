# 📦 Mejores Prácticas: Versionado de Artefactos ML con DVC

## 🎯 ¿Qué son los Artefactos ML?

Los **artefactos ML** son archivos binarios generados durante el proceso de Machine Learning:

- 🔧 **Transformadores**: Encoders, scalers, PCA, etc. (`.pkl`, `.joblib`)
- 🤖 **Modelos entrenados**: XGBoost, LightGBM, redes neuronales (`.pkl`, `.h5`, `.bin`)
- 📊 **Objetos de preprocesamiento**: Vocabularios, tokenizers, etc.

---

## ⚠️ Regla de Oro

| Tipo de Archivo | Manejado por | Razón |
|-----------------|--------------|-------|
| **Archivos `.pkl`, `.joblib`, `.h5`** | ✅ **DVC** | Son binarios y pueden ser grandes |
| **Archivos `.dvc`** (metadatos) | ✅ **Git** | Son pequeños y contienen referencias |
| **Código Python, notebooks** | ✅ **Git** | Son archivos de texto |
| **Archivos CSV grandes** | ✅ **DVC** | Datos grandes |

---

## 🏗️ Estructura Recomendada

```
proyecto/
├── models/
│   ├── encoders/              # 🔧 Transformadores de encoding
│   │   ├── onehot_encoder.pkl
│   │   ├── label_encoder.pkl
│   │   └── ordinal_encoder.pkl
│   │
│   ├── scalers/               # 📏 Normalizadores y escaladores
│   │   ├── standard_scaler.pkl
│   │   └── minmax_scaler.pkl
│   │
│   ├── preprocessors/         # 🔄 Transformadores dimensionales
│   │   ├── pca_model.pkl
│   │   ├── feature_selector.pkl
│   │   └── imputer.pkl
│   │
│   └── trained_models/        # 🤖 Modelos entrenados
│       ├── xgboost_v1.pkl
│       ├── lightgbm_v1.pkl
│       └── nn_model.h5
│
├── models.dvc                 # Archivo DVC que trackea todo /models/
└── .gitignore                 # Ignora *.pkl, *.joblib, *.h5, etc.
```

---

## 📝 Nomenclatura de Artefactos

### Nombres Descriptivos

✅ **Bueno**:
```
onehot_encoder_v1.0.pkl
pca_95_variance.pkl
xgboost_baseline_v1.pkl
lightgbm_optimized_v2.pkl
```

❌ **Malo**:
```
encoder.pkl
model.pkl
final.pkl
final_final_v3.pkl
```

### Incluir Metadata en el Nombre

```python
# Ejemplo de guardado con metadata
encoder_name = f"onehot_encoder_v{VERSION}_{datetime.now().strftime('%Y%m%d')}.pkl"
joblib.dump(encoder, f"../models/encoders/{encoder_name}")
```

---

## 🔄 Flujo de Trabajo: Crear y Versionar

### Paso 1: Entrenar/Crear el Artefacto

```python
from sklearn.preprocessing import OneHotEncoder
import joblib
import os

# Crear encoder
encoder = OneHotEncoder(sparse_output=False, drop='first')
encoder.fit(df[categorical_cols])

# Guardar en directorio apropiado
os.makedirs('../models/encoders', exist_ok=True)
encoder_path = '../models/encoders/onehot_encoder.pkl'
joblib.dump(encoder, encoder_path)

print(f"✅ Encoder guardado: {encoder_path}")
```

### Paso 2: Versionar con DVC

#### Opción A: Versionar directorio completo (RECOMENDADO)

```bash
# Versionar todo el directorio models/
bash add_to_dvc.sh models artifacts-v1.0 'Initial preprocessing artifacts'
```

**Ventajas**:
- ✅ Un solo `.dvc` file maneja todo
- ✅ Todos los artefactos se sincronizan juntos
- ✅ Más simple de mantener

#### Opción B: Versionar archivos individuales

```bash
# Versionar encoder específico
bash add_to_dvc.sh models/encoders/onehot_encoder.pkl encoders-v1.0 'OneHot encoder for categorical features'

# Versionar PCA
bash add_to_dvc.sh models/preprocessors/pca_model.pkl pca-v1.0 'PCA with 95% variance explained'
```

**Ventajas**:
- ✅ Control granular de versiones
- ✅ Puedes recuperar artefactos individuales

**Desventajas**:
- ⚠️ Más archivos `.dvc` para mantener
- ⚠️ Riesgo de desincronización

---

## 🏷️ Convención de Tags

### Para Artefactos de Preprocesamiento

```
artifacts-v<major>.<minor>-<description>

Ejemplos:
- artifacts-v1.0            # Primera versión
- artifacts-v1.1-updated    # Actualización menor
- artifacts-v2.0-redesign   # Rediseño completo
```

### Para Modelos Entrenados

```
models-v<major>.<minor>-<type>

Ejemplos:
- models-v1.0-baseline      # Modelos baseline
- models-v1.1-tuned         # Con hyperparameter tuning
- models-v2.0-ensemble      # Modelos ensemble
```

---

## 📊 Ejemplo Completo: Notebook 2_Data_Processing

### En el Notebook

```python
import os
import joblib
from sklearn.preprocessing import OneHotEncoder
from sklearn.decomposition import PCA

# === 1. Entrenar encoder ===
encoder = OneHotEncoder(sparse_output=False, drop='first')
encoder.fit(df[nominal_variables])

# === 2. Guardar encoder ===
os.makedirs('../models/encoders', exist_ok=True)
encoder_path = '../models/encoders/onehot_encoder.pkl'
joblib.dump(encoder, encoder_path)
print(f"✅ Encoder guardado: {encoder_path}")

# === 3. Entrenar PCA ===
pca = PCA(n_components=0.95)
pca.fit(X_features)

# === 4. Guardar PCA ===
os.makedirs('../models/preprocessors', exist_ok=True)
pca_path = '../models/preprocessors/pca_model.pkl'
joblib.dump(pca, pca_path)
print(f"✅ PCA guardado: {pca_path}")

# === 5. Mostrar instrucciones de versionado ===
print("\n" + "="*70)
print("📦 SIGUIENTE PASO: Versionar con DVC")
print("="*70)
print(f"bash add_to_dvc.sh models artifacts-v1.0 'Preprocessing artifacts: encoder and PCA'")
```

### En la Terminal

```bash
# Ejecutar después de terminar el notebook
cd /Users/hectoralvarez/Documents/GitHub/equipo36mlops

# Versionar todos los artefactos
bash add_to_dvc.sh models artifacts-v1.0 'Preprocessing artifacts: encoder and PCA'

# Verificar
git status
dvc status

# Ver estructura
tree models/
```

**Resultado esperado**:

```
models/
├── encoders/
│   └── onehot_encoder.pkl     # Ignorado por Git, manejado por DVC
├── preprocessors/
│   └── pca_model.pkl          # Ignorado por Git, manejado por DVC
└── models.dvc                 # En Git (metadatos)
```

---

## 🔍 Cargar Artefactos Versionados

### Desde otro compañero del equipo

```bash
# 1. Clonar el repo (si no lo tienes)
git clone <repo-url>
cd equipo36mlops

# 2. Configurar AWS (si no lo has hecho)
bash setup_aws_credentials.sh

# 3. Descargar artefactos
dvc pull

# 4. Verificar que existen
ls -lh models/encoders/
ls -lh models/preprocessors/
```

### En Python

```python
import joblib

# Cargar encoder
encoder = joblib.load('../models/encoders/onehot_encoder.pkl')

# Cargar PCA
pca = joblib.load('../models/preprocessors/pca_model.pkl')

# Usar para transformar nuevos datos
X_encoded = encoder.transform(X_new_categorical)
X_pca = pca.transform(X_new_features)
```

---

## 🔄 Actualizar Artefactos Existentes

### Escenario: Cambiaste el preprocesamiento

```python
# En el notebook, modificaste el encoder
encoder_new = OneHotEncoder(sparse_output=False, drop='first', handle_unknown='ignore')
encoder_new.fit(df[nominal_variables])

# Sobrescribir archivo
joblib.dump(encoder_new, '../models/encoders/onehot_encoder.pkl')
```

### Versionar la actualización

```bash
# DVC detectará el cambio automáticamente
bash add_to_dvc.sh models artifacts-v1.1-updated 'Updated encoder with handle_unknown=ignore'
```

**Lo que pasa internamente**:

1. DVC calcula el nuevo MD5 del archivo
2. Sube la nueva versión a S3
3. Actualiza `models.dvc` con el nuevo hash
4. Git guarda el cambio en `models.dvc`
5. Se crea un nuevo tag `artifacts-v1.1-updated`

---

## 📋 Mejores Prácticas

### ✅ DO (Hacer)

1. **Versionar TODO artefacto que se use en producción**
   ```bash
   dvc add models/encoders/
   dvc add models/trained_models/
   ```

2. **Usar nombres descriptivos**
   ```python
   joblib.dump(model, 'xgboost_baseline_rmse_0.85.pkl')
   ```

3. **Documentar dependencias de versiones**
   ```python
   # Este encoder fue entrenado con data-v1.1-cleaned
   encoder_metadata = {
       'data_version': 'data-v1.1-cleaned',
       'trained_date': '2025-10-13',
       'features': categorical_cols
   }
   joblib.dump({'encoder': encoder, 'metadata': encoder_metadata}, encoder_path)
   ```

4. **Versionar encoder Y datos juntos (tags relacionados)**
   ```bash
   # Primero los datos
   bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned 'Cleaned data'
   
   # Luego los artefactos entrenados CON esos datos
   bash add_to_dvc.sh models/encoders artifacts-v1.1-cleaned 'Artifacts trained with data-v1.1-cleaned'
   ```

### ❌ DON'T (No hacer)

1. **NO versionar con Git**
   ```bash
   # ❌ MALO
   git add models/encoders/onehot_encoder.pkl
   
   # ✅ BUENO
   dvc add models/encoders/onehot_encoder.pkl
   ```

2. **NO guardar en directorios temporales o notebooks/**
   ```python
   # ❌ MALO
   joblib.dump(encoder, 'encoder.pkl')  # En notebook/
   
   # ✅ BUENO
   joblib.dump(encoder, '../models/encoders/onehot_encoder.pkl')
   ```

3. **NO usar nombres genéricos**
   ```python
   # ❌ MALO
   joblib.dump(model, 'model.pkl')
   joblib.dump(model, 'final.pkl')
   
   # ✅ BUENO
   joblib.dump(model, 'xgboost_v1_baseline.pkl')
   ```

4. **NO olvidar hacer dvc push**
   ```bash
   dvc add models/
   git add models.dvc
   git commit -m "Add models"
   # ❌ Si olvidas esto, tus compañeros no tendrán los archivos!
   dvc push  # ✅ CRÍTICO
   ```

---

## 🔧 Comandos Útiles

### Ver qué artefactos están versionados

```bash
# Listar archivos trackeados por DVC
dvc list . -R --dvc-only

# Ver estado de DVC
dvc status

# Ver qué archivos están en S3
aws s3 ls s3://mlops-team36-bucket/equipo36mlops/ --recursive | grep models
```

### Recuperar versión específica de artefactos

```bash
# Cambiar a una versión anterior
git checkout artifacts-v1.0
dvc checkout

# Ver los artefactos de esa versión
ls -lh models/

# Volver a la versión actual
git checkout main
dvc checkout
```

### Comparar tamaños de artefactos entre versiones

```bash
# Ver diferencias entre versiones
dvc diff artifacts-v1.0 artifacts-v1.1-updated

# Ver tamaño de un artefacto específico
ls -lh models/encoders/onehot_encoder.pkl
```

---

## 📊 Ejemplo Real: Pipeline Completo

### Notebook 1: EDA y Limpieza

```python
# Guarda: data/processed/student_performance.csv
df_clean.to_csv('../data/processed/student_performance.csv', index=False)
```

**Versionar**:
```bash
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned 'Dataset after EDA'
```

---

### Notebook 2: Feature Engineering

```python
# Entrena y guarda: encoder, PCA
joblib.dump(encoder, '../models/encoders/onehot_encoder.pkl')
joblib.dump(pca, '../models/preprocessors/pca_model.pkl')

# Guarda: data/processed/student_performance_features.csv
df_features.to_csv('../data/processed/student_performance_features.csv', index=False)
```

**Versionar**:
```bash
# Features
bash add_to_dvc.sh data/processed/student_performance_features.csv data-v1.2-features 'Features with PCA'

# Artefactos (entrenados con data-v1.1-cleaned)
bash add_to_dvc.sh models artifacts-v1.2-features 'Preprocessing artifacts trained with data-v1.1-cleaned'
```

---

### Notebook 3: Model Training

```python
# Entrena y guarda modelos con MLflow (se guarda en data/mlflow/)
# MLflow guarda automáticamente los modelos como artifacts

# Puedes también guardar modelos individuales
joblib.dump(best_model, '../models/trained_models/xgboost_best.pkl')
```

**Versionar**:
```bash
# MLflow completo
bash add_to_dvc.sh data/mlflow models-v1.0-baseline 'Baseline models: LightGBM, XGBoost, CatBoost'

# O modelo específico
bash add_to_dvc.sh models/trained_models trained-models-v1.0 'Best trained models'
```

---

## 🎯 Resumen Ejecutivo

| Paso | Acción | Comando |
|------|--------|---------|
| 1 | Entrenar artefacto | `encoder.fit(X)` |
| 2 | Guardar en `models/` | `joblib.dump(encoder, '../models/encoders/encoder.pkl')` |
| 3 | Versionar con DVC | `bash add_to_dvc.sh models artifacts-v1.0 'Description'` |
| 4 | Compartir con equipo | *Automático con el script* |
| 5 | Descargar en otro equipo | `dvc pull` |
| 6 | Cargar artefacto | `encoder = joblib.load('models/encoders/encoder.pkl')` |

---

## 🆘 Troubleshooting

### Problema: "File too large for Git"

**Causa**: Intentaste hacer `git add` en un archivo `.pkl`

**Solución**:
```bash
# Remover del staging de Git
git rm --cached models/encoders/onehot_encoder.pkl

# Versionar correctamente con DVC
bash add_to_dvc.sh models/encoders/onehot_encoder.pkl encoders-v1.0 'Encoder'
```

---

### Problema: "FileNotFoundError: No such file 'encoder.pkl'"

**Causa**: No descargaste los artefactos con `dvc pull`

**Solución**:
```bash
dvc pull
```

---

### Problema: Artefacto corrupto después de `dvc pull`

**Solución**:
```bash
# Limpiar cache y re-descargar
dvc pull --force
```

---

## 📚 Recursos Adicionales

- [DVC Documentation: Managing Large Files](https://dvc.org/doc/start/data-management)
- [Joblib Documentation](https://joblib.readthedocs.io/)
- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)

---

**Última actualización**: Octubre 2025  
**Equipo 36 MLOps** | Tec de Monterrey

