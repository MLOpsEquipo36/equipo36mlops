# 📦 Sistema de Versionado DVC - Equipo 36 MLOps

## 🎯 Archivo a Versionar

```
data/raw/student_entry_performance.csv
```

---

## ⚡ Inicio Ultra-Rápido (5 minutos)

```bash
# 1. Configurar remote
mkdir -p ~/dvc-storage/equipo36mlops
dvc remote add -d local ~/dvc-storage/equipo36mlops

# 2. Versionar el archivo original
bash setup_dvc.sh data/raw/student_entry_performance.csv
# Tag: data-v1.0-raw

# 3. Subir
dvc push
git push --tags

# 4. Ejecutar primer notebook
jupyter notebook notebooks/1.0-el-EDA_cleaning.ipynb
```

---

## 📊 Pipeline Completo (3 Versiones)

| Versión | Tag | Archivo | Generado por |
|---------|-----|---------|--------------|
| **1.0** | `data-v1.0-raw` | `data/raw/student_entry_performance.csv` | Original |
| **1.1** | `data-v1.1-cleaned` | `data/processed/student_performance.csv` | Notebook EDA |
| **1.2** | `data-v1.2-features` | `data/processed/student_performance_features.csv` | Notebook Preprocessing |

---

## 🛠️ Scripts Disponibles

### `setup_dvc.sh` - Primera configuración

```bash
# Modo interactivo (te muestra opciones)
bash setup_dvc.sh

# Modo directo (especificas archivo)
bash setup_dvc.sh data/raw/student_entry_performance.csv
```

### `add_to_dvc.sh` - Agregar archivos rápido

```bash
# Con tag y descripción
bash add_to_dvc.sh <archivo> <tag> "descripción"

# Ejemplo
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned "After EDA"
```

---

## 📚 Documentación (por nivel)

### 🟢 Principiante (Empieza aquí)
1. **`DVC_QUICKSTART.md`** (2 min) - 5 pasos simples
2. **`RESUMEN_FINAL.md`** (5 min) - Tu guía específica

### 🟡 Intermedio
3. **`DVC_WORKFLOW.md`** (15 min) - Flujo completo actualizado
4. **`GUIA_SETUP_DVC.md`** (20 min) - Guía detallada de scripts

---

## 🔄 Comandos Útiles

```bash
# Ver versiones
git tag -l "data-*"

# Cambiar a versión anterior
git checkout data-v1.0-raw && dvc checkout

# Volver a la última
git checkout main && dvc checkout

# Sincronizar con equipo
dvc pull

# Ver estado
dvc status
```

---

## ✅ Checklist

- [ ] Remote configurado
- [ ] `student_entry_performance.csv` versionado (v1.0-raw)
- [ ] Notebook EDA ejecutado
- [ ] `student_performance.csv` versionado (v1.1-cleaned)
- [ ] Notebook Preprocessing ejecutado
- [ ] `student_performance_features.csv` versionado (v1.2-features)
- [ ] Todo subido con `dvc push` y `git push --tags`

---

## 🚀 Siguiente Paso

```bash
bash setup_dvc.sh data/raw/student_entry_performance.csv
```

**Documentación completa:** Ver archivos `.md` listados arriba.

¡Tu sistema de versionado está listo! 🎉

