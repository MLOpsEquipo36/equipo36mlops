# 🚀 Inicio Rápido - Versionado de tu Dataset

## 📁 Tu Situación Actual

Tienes un solo archivo fuente:
```
data/raw/student_entry_performance.csv
```

Este archivo será procesado por dos notebooks secuencialmente:
1. `1.0-el-EDA_cleaning.ipynb` → limpieza y EDA
2. `Preprocesamieto de Datos.ipynb` → feature engineering

---

## 🎯 Flujo Completo (3 Versiones)

```
Version 1.0 (raw)
    ↓
[Notebook 1: EDA + Limpieza]
    ↓
Version 1.1 (cleaned)
    ↓
[Notebook 2: Feature Engineering]
    ↓
Version 1.2 (features)
```

---

## ⚡ Paso a Paso

### 🔹 Paso 0: Configuración Inicial (Una sola vez)

```bash
# Configurar remote local para DVC
mkdir -p ~/dvc-storage/equipo36mlops
dvc remote add -d local ~/dvc-storage/equipo36mlops
git add .dvc/config
git commit -m "chore: configure DVC local remote"
```

---

### 🔹 Paso 1: Versionar el Dataset Original

```bash
# Versionar el archivo RAW
bash setup_dvc.sh data/raw/student_entry_performance.csv
```

**Durante el script:**
- Remote: Selecciona "3" (skip - ya lo configuraste)
- Tag: `data-v1.0-raw`
- Descripción: `Raw dataset from source`

**Luego:**
```bash
dvc push
git push --tags
```

**✅ Resultado:** `data/raw/student_entry_performance.csv` está versionado

---

### 🔹 Paso 2: Ejecutar Notebook de EDA

```bash
# Abrir el notebook
jupyter notebook notebooks/1.0-el-EDA_cleaning.ipynb

# O con JupyterLab
jupyter lab notebooks/1.0-el-EDA_cleaning.ipynb
```

**El notebook:**
1. Lee: `data/raw/student_entry_performance.csv`
2. Aplica limpieza (mayúsculas, trim, manejo de nulls, etc.)
3. Guarda: `data/processed/student_performance.csv`
4. Te muestra comandos para versionar

**Al finalizar el notebook, ejecuta:**
```bash
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned "After EDA cleaning"
dvc push
git push --tags
```

**✅ Resultado:** `data/processed/student_performance.csv` versionado (datos limpios)

---

### 🔹 Paso 3: Ejecutar Notebook de Preprocessing

```bash
# Abrir el segundo notebook
jupyter notebook notebooks/Preprocesamieto\ de\ Datos.ipynb
```

**El notebook:**
1. Lee: `data/processed/student_performance.csv` (versión limpia)
2. Aplica: Chi-cuadrada, Spearman, One-Hot Encoding, PCA
3. Guarda: `data/processed/student_performance_features.csv`
4. Te muestra comandos para versionar

**Al finalizar el notebook, ejecuta:**
```bash
bash add_to_dvc.sh data/processed/student_performance_features.csv data-v1.2-features "Features with PCA ready for modeling"
dvc push
git push --tags
```

**✅ Resultado:** Features listas para entrenar modelos

---

## 📊 Estructura Final

```
data/
├── raw/
│   └── student_entry_performance.csv        [DVC: data-v1.0-raw]
└── processed/
    ├── student_performance.csv              [DVC: data-v1.1-cleaned]
    └── student_performance_features.csv     [DVC: data-v1.2-features]
```

---

## 🔄 Comandos Útiles

### Ver todas las versiones
```bash
git tag -l "data-*"
```

### Recuperar versión específica
```bash
# Cambiar a una versión anterior
git checkout data-v1.0-raw
dvc checkout

# Ver el archivo
head data/raw/student_entry_performance.csv

# Volver a la última versión
git checkout main
dvc checkout
```

### Sincronizar con tu equipo
```bash
# Tu compañero descarga todo
git pull
dvc pull

# Ya tiene todos los datasets en las versiones correctas
```

### Ver estado actual
```bash
dvc status
git status
```

---

## 🎓 Resumen de Comandos

| Acción | Comando |
|--------|---------|
| **Primera vez:** Versionar raw | `bash setup_dvc.sh data/raw/student_entry_performance.csv` |
| **Después EDA:** Versionar cleaned | `bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned "Clean"` |
| **Después Features:** Versionar features | `bash add_to_dvc.sh data/processed/student_performance_features.csv data-v1.2-features "Features"` |
| Subir a remote | `dvc push` |
| Descargar de remote | `dvc pull` |
| Ver versiones | `git tag -l` |
| Cambiar versión | `git checkout <tag> && dvc checkout` |

---

## ✅ Checklist de Progreso

- [ ] Paso 0: Remote de DVC configurado
- [ ] Paso 1: `student_entry_performance.csv` versionado (data-v1.0-raw)
- [ ] Paso 2: Notebook EDA ejecutado
- [ ] Paso 2: `student_performance.csv` versionado (data-v1.1-cleaned)
- [ ] Paso 3: Notebook Preprocessing ejecutado
- [ ] Paso 3: `student_performance_features.csv` versionado (data-v1.2-features)
- [ ] Todo subido: `dvc push` y `git push --tags`

---

## 🆘 Problemas Comunes

### "FileNotFoundError: student_entry_performance.csv"
```bash
# Verifica que el archivo existe
ls -la data/raw/student_entry_performance.csv

# Si no existe, revisa si tiene otro nombre
ls -la data/raw/
```

### "dvc: command not found"
```bash
pip install dvc
```

### El notebook no encuentra el archivo
```bash
# Asegúrate de ejecutar desde la raíz del proyecto
cd /Users/hectoralvarez/Documents/GitHub/equipo36mlops
jupyter notebook
```

---

## 🎉 ¡Listo!

Ahora tienes un pipeline de datos completamente versionado:

1. **Data Raw** (v1.0) → Original sin modificar
2. **Data Cleaned** (v1.1) → Después de EDA
3. **Data Features** (v1.2) → Listo para modelado

Puedes volver a cualquier versión en cualquier momento con Git + DVC.

**Siguiente paso:** Entrenar modelos usando `student_performance_features.csv` 🚀

