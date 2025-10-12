# 🚀 Quick Start: Versionado con DVC

## 📁 Tu Archivo

```
data/raw/student_entry_performance.csv
```

Este archivo será procesado por 2 notebooks creando 3 versiones.

---

## ⚡ Pasos Rápidos

### 1. Configurar Remote (una vez)

```bash
mkdir -p ~/dvc-storage/equipo36mlops
dvc remote add -d local ~/dvc-storage/equipo36mlops
git add .dvc/config
git commit -m "chore: configure DVC local remote"
```

### 2. Versionar Archivo Original

```bash
bash setup_dvc.sh data/raw/student_entry_performance.csv
```
**Tag:** `data-v1.0-raw`

### 3. Ejecutar Notebook 1 (EDA)

```bash
jupyter notebook notebooks/1.0-el-EDA_cleaning.ipynb
```

Luego versionar:
```bash
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned "After EDA"
```

### 4. Ejecutar Notebook 2 (Features)

```bash
jupyter notebook notebooks/Preprocesamieto\ de\ Datos.ipynb
```

Luego versionar:
```bash
bash add_to_dvc.sh data/processed/student_performance_features.csv data-v1.2-features "Features"
```

### 5. Subir Todo

```bash
dvc push
git push --tags
```

---

## 📊 Resultado Final

Tendrás 3 versiones:

| Tag | Archivo | Descripción |
|-----|---------|-------------|
| `data-v1.0-raw` | `data/raw/student_entry_performance.csv` | Original |
| `data-v1.1-cleaned` | `data/processed/student_performance.csv` | Limpio |
| `data-v1.2-features` | `data/processed/student_performance_features.csv` | Features |

---

## 🔄 Comandos Útiles

```bash
# Ver versiones
git tag -l "data-*"

# Volver a una versión
git checkout data-v1.0-raw
dvc checkout

# Volver a la última
git checkout main
dvc checkout

# Sincronizar con equipo
dvc pull
```

---

## 📚 Documentación Completa

| Archivo | Para qué |
|---------|----------|
| `RESUMEN_FINAL.md` ⭐ | Tu guía paso a paso |
| `DVC_WORKFLOW.md` | Flujo completo actualizado |
| `GUIA_SETUP_DVC.md` | Guía detallada de scripts |

---

## 🎯 Siguiente Paso

```bash
bash setup_dvc.sh data/raw/student_entry_performance.csv
```

¡Listo! 🎉
