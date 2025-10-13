# 🎓 Ejemplo de Uso Completo: Pipeline MLOps con DVC

Este documento muestra un ejemplo completo de cómo usar el pipeline de notebooks con versionado DVC.

---

## 📋 Escenario

Eres un miembro del Equipo 36 y vas a trabajar en el proyecto desde cero. Seguirás estos pasos:

1. Configurar el ambiente
2. Ejecutar los 3 notebooks
3. Versionar los datos en cada paso
4. Compartir tu trabajo con el equipo

---

## 🛠️ Paso 0: Configuración Inicial (solo una vez)

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/equipo36mlops.git
cd equipo36mlops
```

### 2. Instalar dependencias

```bash
# Crear ambiente virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar AWS (para DVC)

```bash
# Ejecutar el script de configuración
bash setup_aws_credentials.sh

# Cuando te pida, ingresa:
# - AWS Access Key ID: [tu-access-key]
# - AWS Secret Access Key: [tu-secret-key]
# - Region: us-east-2
```

### 4. Verificar configuración de DVC

```bash
# Ver configuración de DVC
cat .dvc/config

# Debería mostrar:
# [core]
#     remote = s3remote
# ['remote "s3remote"']
#     url = s3://mlops-team36-bucket/equipo36mlops
#     region = us-east-2
```

### 5. Descargar datos existentes (si ya existen)

```bash
# Si el equipo ya ha versionado datos
dvc pull

# Verificar que los datos se descargaron
ls -lh data/raw/
```

---

## 📊 Paso 1: Ejecutar Notebook 1 - EDA y Limpieza

### 1.1. Antes de empezar

```bash
# Asegúrate de tener la última versión del código
git pull

# Asegúrate de tener los datos raw
dvc pull
```

### 1.2. Abrir y ejecutar el notebook

```bash
# Abrir Jupyter
jupyter notebook notebooks/1_EDA_and_Cleaning.ipynb

# O si usas JupyterLab
jupyter lab notebooks/1_EDA_and_Cleaning.ipynb
```

**Ejecuta todas las celdas del notebook.** Al final, el notebook:
- Lee: `data/raw/student_entry_performance.csv`
- Guarda: `data/processed/student_performance.csv`
- Muestra instrucciones de versionado

### 1.3. Versionar el resultado

```bash
# Volver a la terminal
cd /Users/hectoralvarez/Documents/GitHub/equipo36mlops

# Ejecutar el comando que el notebook te mostró
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned 'Dataset after EDA cleaning'
```

**Salida esperada**:

```
======================================================================
   📦 DVC Data Versioning Helper - Equipo 36 MLOps
======================================================================

ℹ️  Archivo a versionar: data/processed/student_performance.csv
ℹ️  Tag: data-v1.1-cleaned
ℹ️  Mensaje: Dataset after EDA cleaning

----------------------------------------------------------------------
ℹ️  PASO 1: Verificando estado del archivo...
----------------------------------------------------------------------
ℹ️  Agregando archivo nuevo a DVC...
✅ Archivo agregado a DVC

----------------------------------------------------------------------
ℹ️  PASO 2: Agregando metadatos DVC a Git...
----------------------------------------------------------------------
✅ Metadatos agregados a Git

----------------------------------------------------------------------
ℹ️  PASO 3: Creando commit...
----------------------------------------------------------------------
[main abc1234] feat: version data - Dataset after EDA cleaning
 2 files changed, 8 insertions(+)
 create mode 100644 data/processed/student_performance.csv.dvc

----------------------------------------------------------------------
ℹ️  PASO 4: Creando tag Git...
----------------------------------------------------------------------
✅ Tag creado: data-v1.1-cleaned

----------------------------------------------------------------------
ℹ️  PASO 5: Subiendo datos a DVC remote (S3)...
----------------------------------------------------------------------
1 file pushed
✅ Datos subidos a S3

----------------------------------------------------------------------
ℹ️  PASO 6: Subiendo metadatos y tags a Git remote...
----------------------------------------------------------------------
✅ Push completado

======================================================================
✅ VERSIONADO COMPLETADO
======================================================================

ℹ️  Resumen:
  📁 Archivo:     data/processed/student_performance.csv
  🏷️  Tag:         data-v1.1-cleaned
  📝 Descripción: Dataset after EDA cleaning

ℹ️  Para recuperar esta versión en el futuro:
  git checkout data-v1.1-cleaned
  dvc checkout

✅ ¡Listo! Tus datos están versionados correctamente.
======================================================================
```

### 1.4. Verificar que todo funcionó

```bash
# Ver que el archivo .dvc se creó
ls -l data/processed/

# Deberías ver:
# student_performance.csv
# student_performance.csv.dvc

# Ver el contenido del archivo .dvc
cat data/processed/student_performance.csv.dvc

# Ver que el tag se creó
git tag -l

# Deberías ver:
# data-v1.1-cleaned
```

---

## 🔧 Paso 2: Ejecutar Notebook 2 - Feature Engineering

### 2.1. Antes de empezar

```bash
# Asegúrate de tener la versión limpia de los datos
dvc pull

# Verificar que el archivo existe
ls -lh data/processed/student_performance.csv
```

### 2.2. Abrir y ejecutar el notebook

```bash
jupyter notebook notebooks/2_Data_Processing.ipynb
```

**Ejecuta todas las celdas del notebook.** Al final, el notebook:
- Lee: `data/processed/student_performance.csv`
- Aplica: Feature selection, encoding, PCA
- Guarda: `data/processed/student_performance_features.csv`
- Guarda: `onehot_encoder.pkl` (encoder para uso posterior)

### 2.3. Versionar el resultado

```bash
# Ejecutar el comando que el notebook te mostró
bash add_to_dvc.sh data/processed/student_performance_features.csv data-v1.2-features 'Features with PCA ready for modeling'
```

### 2.4. Versionar también el encoder (opcional pero recomendado)

```bash
# Mover el encoder al directorio de modelos
mkdir -p models/encoders
mv onehot_encoder.pkl models/encoders/

# Versionarlo con DVC
bash add_to_dvc.sh models/encoders/onehot_encoder.pkl encoders-v1.0 'OneHot encoder for nominal variables'
```

---

## 🤖 Paso 3: Ejecutar Notebook 3 - Entrenamiento de Modelos

### 3.1. Antes de empezar

```bash
# Asegúrate de tener las features
dvc pull

# Verificar que el archivo existe
ls -lh data/processed/student_performance_features.csv
```

### 3.2. Abrir y ejecutar el notebook

```bash
jupyter notebook notebooks/3_Model_Training_and_Registering.ipynb
```

**Ejecuta todas las celdas del notebook.** El notebook:
- Lee: `data/processed/student_performance_features.csv`
- Entrena: LightGBM, XGBoost, CatBoost
- Registra: Experimentos en MLflow (directorio `data/mlflow/`)
- Calcula: Métricas RMSE y QWK

### 3.3. Ver experimentos en MLflow (opcional)

Si ejecutaste la celda que levanta el servidor de MLflow:

```bash
# Abrir en el navegador
# http://127.0.0.1:8080

# Ahí podrás ver:
# - Todos los experimentos
# - Métricas de cada modelo
# - Parámetros usados
# - Comparación entre modelos
```

### 3.4. Versionar los modelos

```bash
# Ejecutar el comando que el notebook te mostró
bash add_to_dvc.sh data/mlflow models-v1.0-baseline 'Baseline models: LightGBM, XGBoost, CatBoost'
```

---

## 🎉 Paso 4: Verificar el Pipeline Completo

### 4.1. Ver todas las versiones creadas

```bash
# Listar todos los tags
git tag -l

# Deberías ver:
# data-v1.0-raw            (ya existía)
# data-v1.1-cleaned        (creado en Paso 1)
# data-v1.2-features       (creado en Paso 2)
# encoders-v1.0            (creado en Paso 2 opcional)
# models-v1.0-baseline     (creado en Paso 3)
```

### 4.2. Ver el historial de commits

```bash
git log --oneline --all --graph --decorate

# Deberías ver algo como:
# * def5678 (tag: models-v1.0-baseline) feat: version models - baseline models trained
# * abc1234 (tag: data-v1.2-features) feat: version data - features engineered
# * xyz9876 (tag: data-v1.1-cleaned) feat: version data - dataset after EDA
```

### 4.3. Ver qué archivos están en S3

```bash
# Ver archivos en el bucket S3
aws s3 ls s3://mlops-team36-bucket/equipo36mlops/ --recursive

# O usando DVC
dvc list -R . --dvc-only
```

---

## 👥 Paso 5: Compartir con el Equipo

Tu trabajo ya está en Git y S3. Ahora tus compañeros pueden descargarlo.

### 5.1. Avisar al equipo

Envía un mensaje a tu equipo:

```
¡Hola equipo! 👋

Acabo de completar el pipeline hasta el entrenamiento de modelos baseline.

Versiones creadas:
✅ data-v1.1-cleaned: Dataset después de EDA
✅ data-v1.2-features: Features con PCA
✅ models-v1.0-baseline: Modelos LightGBM, XGBoost, CatBoost

Para obtener todo:
1. git pull
2. dvc pull

Para ver los experimentos de MLflow:
cd /Users/hectoralvarez/Documents/GitHub/equipo36mlops
mlflow ui --backend-store-uri file:./data/mlflow
# Abrir http://localhost:5000

¡Pueden empezar a trabajar con estos modelos! 🚀
```

---

## 🔄 Paso 6: Recuperar una Versión Anterior (Ejemplo)

Supongamos que quieres volver a la versión de datos limpios (sin features).

### 6.1. Cambiar a esa versión

```bash
# Cambiar a la versión de datos limpios
git checkout data-v1.1-cleaned

# Descargar los datos de esa versión
dvc checkout

# Ver el archivo
head data/processed/student_performance.csv

# ✅ Ahora tienes los datos tal como estaban después del EDA
```

### 6.2. Experimentar con esa versión

```bash
# Puedes abrir un notebook y experimentar
jupyter notebook notebooks/2_Data_Processing.ipynb

# Modificar parámetros, probar diferentes transformaciones, etc.
```

### 6.3. Volver al estado actual

```bash
# Volver a la rama principal
git checkout main

# Descargar los datos más recientes
dvc checkout

# ✅ Ahora tienes la última versión de todo
```

---

## 🔍 Paso 7: Comparar Versiones (Ejemplo Avanzado)

### 7.1. Comparar dos versiones de datos

```bash
# Ver diferencias en metadatos (tamaño, hash)
dvc diff data-v1.1-cleaned data-v1.2-features

# Salida esperada:
# Path                                      Metric    Old       New     Change
# data/processed/student_performance.csv    size      150KB     -       deleted
# data/processed/student_performance_features.csv  size    -    25KB    added
```

### 7.2. Extraer ambas versiones para comparación manual

```bash
# Crear directorio temporal
mkdir -p /tmp/comparison

# Extraer versión 1.1
git checkout data-v1.1-cleaned
dvc checkout
cp data/processed/student_performance.csv /tmp/comparison/v1.1.csv

# Extraer versión 1.2
git checkout data-v1.2-features
dvc checkout
cp data/processed/student_performance_features.csv /tmp/comparison/v1.2.csv

# Volver a la versión actual
git checkout main
dvc checkout

# Comparar con Python
python3 << EOF
import pandas as pd

df_v11 = pd.read_csv('/tmp/comparison/v1.1.csv')
df_v12 = pd.read_csv('/tmp/comparison/v1.2.csv')

print(f"v1.1 - Shape: {df_v11.shape}")
print(f"v1.2 - Shape: {df_v12.shape}")
print(f"\nv1.1 columns: {df_v11.columns.tolist()}")
print(f"\nv1.2 columns: {df_v12.columns.tolist()}")
EOF
```

---

## 🚨 Troubleshooting: Problemas Comunes

### Problema 1: "dvc pull" no descarga nada

**Causa**: Puede que no haya archivos nuevos para descargar, o que ya los tengas.

**Solución**:
```bash
# Ver estado
dvc status

# Si dice "Data and pipelines are up to date", está todo bien

# Si quieres forzar la descarga
dvc pull --force
```

---

### Problema 2: "No remote storage is configured"

**Causa**: DVC no sabe dónde está tu S3.

**Solución**:
```bash
# Ver configuración actual
dvc remote list

# Si no aparece nada, configurar:
dvc remote add -d s3remote s3://mlops-team36-bucket/equipo36mlops
dvc remote modify s3remote region us-east-2
```

---

### Problema 3: "Unable to find credentials"

**Causa**: AWS CLI no tiene credenciales configuradas.

**Solución**:
```bash
# Opción 1: Ejecutar el script
bash setup_aws_credentials.sh

# Opción 2: Configurar manualmente
aws configure
```

---

### Problema 4: El notebook no encuentra el archivo de datos

**Causa**: No has descargado los datos con `dvc pull`.

**Solución**:
```bash
# Descargar datos
dvc pull

# Verificar que el archivo existe
ls -lh data/processed/student_performance.csv
```

---

### Problema 5: "Tag already exists"

**Causa**: Estás intentando crear un tag que ya existe.

**Solución**:
```bash
# Opción 1: Usar un tag diferente con versión patch
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1.1-cleaned 'Updated cleaning'

# Opción 2: Borrar y recrear (usar con precaución)
git tag -d data-v1.1-cleaned
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned 'Dataset after EDA cleaning'
```

---

## 📚 Recursos de Ayuda

- **Guía completa**: `docs/DVC_WORKFLOW.md`
- **Comandos rápidos**: `DVC_COMMANDS.md`
- **Guía de notebooks**: `notebooks/README_DVC.md`
- **Documentación DVC**: https://dvc.org/doc

---

## ✅ Checklist Final

Después de completar este ejemplo, deberías tener:

- [x] Ambiente configurado con AWS y DVC
- [x] Los 3 notebooks ejecutados
- [x] 4-5 versiones de datos creadas y subidas a S3
- [x] Modelos entrenados y versionados
- [x] Todo el trabajo compartido con el equipo via Git+DVC
- [x] Capacidad de recuperar cualquier versión anterior

---

**¡Felicidades! Has completado el flujo completo de MLOps con versionado de datos. 🎉**

---

**Equipo 36 MLOps** | Octubre 2025

