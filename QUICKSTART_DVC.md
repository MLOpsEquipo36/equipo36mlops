# 🚀 Quick Start: Configuración de DVC

## 🎯 Scripts Disponibles

Este proyecto incluye scripts para facilitar el versionado con DVC:

| Script | Propósito | Cuándo Usar |
|--------|-----------|-------------|
| `setup_dvc.sh` | Setup completo + versionar primer archivo | Primera vez configurando DVC |
| `add_to_dvc.sh` | Agregar/actualizar archivo rápidamente | Ya tienes DVC configurado |

---

## Opción 1: Usar el Script Automático (Recomendado)

### Modo Interactivo
```bash
# El script te mostrará todos los CSV disponibles y podrás elegir
bash setup_dvc.sh
```

### Modo Directo (con argumento)
```bash
# Especifica directamente qué archivo versionar
bash setup_dvc.sh data/raw/student_entry_performance_original.csv
```

El script te guiará paso a paso para:
- ✅ Verificar instalación de DVC
- ✅ Configurar remote (local o Google Drive)
- ✅ Preparar dataset inicial
- ✅ Crear primera versión (data-v0.1-raw)

---

## Opción 2: Configuración Manual

### 1️⃣ Configurar Remote de DVC

**Opción A: Local (desarrollo)**
```bash
mkdir -p ~/dvc-storage/equipo36mlops
dvc remote add -d local ~/dvc-storage/equipo36mlops
```

**Opción B: Google Drive (colaboración)**
```bash
# Crear carpeta en Google Drive y obtener el ID de la URL
dvc remote add -d gdrive gdrive://TU_FOLDER_ID_AQUI
dvc remote modify gdrive gdrive_acknowledge_abuse true
```

### 2️⃣ Preparar Dataset Inicial

```bash
# Copiar el dataset original
cp data/raw/student_entry_performance_original.csv data/processed/student_performance.csv

# Agregar a DVC
dvc add data/processed/student_performance.csv

# Commitear a Git
git add data/processed/student_performance.csv.dvc data/processed/.gitignore
git commit -m "feat: add initial dataset version to DVC"
git tag -a "data-v0.1-raw" -m "Version 0.1: Raw original data"

# Subir a remote
dvc push
```

### 3️⃣ Ejecutar Notebook de EDA

Abre y ejecuta: `notebooks/1.0-el-EDA_cleaning.ipynb`

Al finalizar, el notebook te mostrará los comandos para versionar los cambios.

### 4️⃣ Versionar Dataset Limpio

```bash
# DVC detecta automáticamente los cambios
dvc add data/processed/student_performance.csv

# Commitear nueva versión
git add data/processed/student_performance.csv.dvc
git commit -m "feat: apply EDA cleaning - normalize text, handle nulls"
git tag -a "data-v0.2-cleaned" -m "Version 0.2: Data after EDA cleaning"

# Subir cambios
dvc push
git push && git push --tags
```

### 5️⃣ Ejecutar Notebook de Preprocessing

Abre y ejecuta: `notebooks/Preprocesamieto de Datos.ipynb`

Esto generará: `data/processed/student_performance_features.csv`

### 6️⃣ Versionar Dataset de Features

```bash
dvc add data/processed/student_performance_features.csv
git add data/processed/student_performance_features.csv.dvc
git commit -m "feat: add engineered features with PCA and encoding"
git tag -a "data-v0.3-features" -m "Version 0.3: Features ready for modeling"
dvc push
git push && git push --tags
```

---

## 📊 Estructura Final

```
data/
├── raw/
│   └── student_entry_performance_original.csv    # Original (sin tocar)
└── processed/
    ├── student_performance.csv                    # Versionado: raw → cleaned
    └── student_performance_features.csv           # Versionado: features

Versiones en Git:
├── data-v0.1-raw        → student_performance.csv (original)
├── data-v0.2-cleaned    → student_performance.csv (después EDA)
└── data-v0.3-features   → student_performance_features.csv
```

---

## 🔄 Comandos Útiles

### Ver historial de versiones
```bash
git log --oneline --tags
```

### Cambiar a versión anterior
```bash
# Volver a versión raw
git checkout data-v0.1-raw
dvc checkout

# Ver el archivo (ahora tiene datos raw)
head data/processed/student_performance.csv

# Volver a última versión
git checkout main
dvc checkout
```

### Sincronizar con equipo
```bash
# Descargar última versión
git pull
dvc pull

# Subir cambios
dvc push
git push
```

---

## ❓ Solución de Problemas

### "dvc: command not found"
```bash
pip install dvc
```

### "No DVC files to upload"
Primero necesitas configurar un remote:
```bash
dvc remote list  # Ver remotes configurados
dvc remote add -d local ~/dvc-storage/equipo36mlops
```

### "File not found: student_performance.csv"
Ejecuta primero el setup:
```bash
bash setup_dvc.sh
```

---

## 📚 Documentación Completa

Ver `DVC_WORKFLOW.md` para explicación detallada del flujo completo.

