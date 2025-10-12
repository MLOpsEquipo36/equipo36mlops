# 🚀 Quick Start: Versionado con DVC

## ⚠️ ACLARACIÓN IMPORTANTE

**TUS ARCHIVOS SE QUEDAN EN `data/`** ✅

DVC NO mueve tus archivos. Solo:
- ✅ Crea archivos `.dvc` con metadatos (van a Git)
- ✅ Guarda copias en `.dvc/cache/` para historial
- ✅ Opcionalmente hace respaldo en remote (OPCIONAL)

**Tu carpeta `data/` ya está lista, no necesitas cambiar nada.**

---

## 📁 Tu Archivo

```
data/raw/student_entry_performance.csv  ← Se queda aquí siempre
```

Este archivo será procesado por 2 notebooks creando 3 versiones.

---

## ⚡ Pasos Rápidos

### Opción A: Sin Remote (Recomendado para empezar) ⭐

```bash
# Versiona directamente, sin configurar remote
bash setup_dvc.sh data/raw/student_entry_performance.csv

# Cuando pregunte por remote: selecciona opción 3 (skip)
# Tag: data-v1.0-raw
```

**Resultado:** Archivo versionado, se queda en `data/raw/` ✅

---

### Opción B: Con Remote Local (Respaldo adicional)

```bash
# 1. Configurar remote (una vez) - OPCIONAL
mkdir -p ~/dvc-storage/equipo36mlops
dvc remote add -d local ~/dvc-storage/equipo36mlops
git add .dvc/config
git commit -m "chore: configure DVC local remote"
```

**Nota:** El remote es solo un RESPALDO. Tus archivos siguen en `data/`.

### 2. Versionar Archivo Original

```bash
bash setup_dvc.sh data/raw/student_entry_performance.csv
```

**Durante el script:**
- Remote: **Opción 3 (skip)** ← No necesitas remote para empezar
- Tag: `data-v1.0-raw`
- Descripción: `Raw dataset from source`

**¿Qué pasa con tu archivo?**
- ✅ Se queda en `data/raw/` (NO se mueve)
- ✅ Se crea `data/raw/student_entry_performance.csv.dvc` (metadatos)
- ✅ Se actualiza `data/raw/.gitignore` (para que Git ignore el CSV)

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

### 5. Subir a Git

```bash
# Subir tags a Git
git push --tags

# Si configuraste remote, también:
dvc push  # OPCIONAL - solo si tienes remote configurado
```

**Nota:** Si NO configuraste remote (opción 3), NO necesitas `dvc push`. Solo `git push --tags`.

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
