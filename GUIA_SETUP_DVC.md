# 📖 Guía de Uso: setup_dvc.sh

## 🎯 Descripción

El script `setup_dvc.sh` es una herramienta flexible para versionar datasets con DVC. Puede funcionar en modo interactivo o con argumentos de línea de comandos.

---

## 🚀 Modos de Uso

### 1️⃣ Modo Interactivo (Recomendado para principiantes)

Ejecuta el script sin argumentos y te guiará paso a paso:

```bash
bash setup_dvc.sh
```

**El script te mostrará:**
1. Lista de todos los archivos CSV en el proyecto
2. Opción para seleccionar de la lista o ingresar ruta manualmente
3. Configuración de remote (local o Google Drive)
4. Opción de crear tags de versión

**Ejemplo de salida:**
```
Archivos CSV disponibles en el proyecto:

  1) data/raw/student_entry_performance.csv  (52K)
  2) data/processed/student_performance.csv  (53K)
  3) data/processed/student_performance_features.csv  (45K)

  0) Ingresar ruta manualmente

Selecciona el archivo a versionar [1-3] o 0: _
```

---

### 2️⃣ Modo Directo (Recomendado para usuarios avanzados)

Especifica directamente el archivo que quieres versionar:

```bash
bash setup_dvc.sh <ruta_del_archivo>
```

**Ejemplos:**

#### Versionar archivo en `raw/` (tu caso):
```bash
bash setup_dvc.sh data/raw/student_entry_performance.csv
```

#### Versionar archivo en `processed/`:
```bash
bash setup_dvc.sh data/processed/student_performance.csv
```

#### Versionar cualquier CSV:
```bash
bash setup_dvc.sh data/interim/mi_dataset_intermedio.csv
bash setup_dvc.sh models/predictions.csv
```

---

## 📋 Casos de Uso Comunes

### Caso 1: Versionar tu Dataset Original en raw/ (TU CASO ⭐)

Este es tu caso específico: tienes `student_entry_performance.csv` en `data/raw/`

```bash
# Versionar el dataset original
bash setup_dvc.sh data/raw/student_entry_performance.csv
```

**¿Qué hace el script?**
- ✅ Agrega el archivo a DVC (crea `student_entry_performance.csv.dvc`)
- ✅ Actualiza `.gitignore` en `data/raw/` (para que Git ignore el CSV)
- ✅ Hace commit a Git del archivo `.dvc`
- ✅ Te pregunta si quieres crear un tag → Responde: `data-v1.0-raw`
- ✅ Configura remote si es primera vez

**Resultado:** Tu archivo está versionado y listo para ser procesado por los notebooks.

---

### Caso 2: Versionar Dataset Procesado (Después de EDA)

Después de ejecutar `1.0-el-EDA_cleaning.ipynb`:

```bash
# Versionar el dataset limpio generado por el notebook
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned "After EDA cleaning"
```

**Resultado:** Dataset limpio versionado y listo para el siguiente paso.

---

### Caso 3: Versionar Features (Después de Preprocessing)

Después de ejecutar `Preprocesamieto de Datos.ipynb`:

```bash
# Versionar las features generadas
bash add_to_dvc.sh data/processed/student_performance_features.csv data-v1.2-features "Features with PCA"
```

**Resultado:** Features listas para entrenar modelos.

---

### Caso 4: Versionar Múltiples Archivos (Pipeline Completo)

Ejecuta el pipeline completo:

```bash
# 1. Versionar el original
bash setup_dvc.sh data/raw/student_entry_performance.csv
# Tag: data-v1.0-raw

# 2. Ejecutar notebook de EDA
jupyter notebook notebooks/1.0-el-EDA_cleaning.ipynb

# 3. Versionar resultado de EDA
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned "After EDA"

# 4. Ejecutar notebook de preprocessing
jupyter notebook notebooks/Preprocesamieto\ de\ Datos.ipynb

# 5. Versionar features
bash add_to_dvc.sh data/processed/student_performance_features.csv data-v1.2-features "With PCA"

# 6. Subir todo
dvc push
git push --tags
```

**Resultado:** Pipeline completo versionado con 3 versiones de datos.

---

## 🎨 Flujo Completo: Tu Proyecto

### Pipeline completo del proyecto equipo36mlops

```bash
# ============================================================================
# PASO 0: Configurar remote (una sola vez)
# ============================================================================
mkdir -p ~/dvc-storage/equipo36mlops
dvc remote add -d local ~/dvc-storage/equipo36mlops
git add .dvc/config
git commit -m "chore: configure DVC local remote"

# ============================================================================
# PASO 1: Versionar dataset original (v1.0-raw)
# ============================================================================
bash setup_dvc.sh data/raw/student_entry_performance.csv

# Durante el script:
# - Remote: opción 3 (skip - ya lo configuraste)
# - Tag: data-v1.0-raw
# - Descripción: Raw dataset from source

dvc push
git push --tags

# ============================================================================
# PASO 2: Ejecutar EDA y versionar resultado (v1.1-cleaned)
# ============================================================================

# Ejecutar notebook de EDA
jupyter notebook notebooks/1.0-el-EDA_cleaning.ipynb

# Versionar el resultado
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned "After EDA cleaning"

dvc push
git push --tags

# ============================================================================
# PASO 3: Ejecutar preprocessing y versionar features (v1.2-features)
# ============================================================================

# Ejecutar notebook de preprocessing
jupyter notebook notebooks/Preprocesamieto\ de\ Datos.ipynb

# Versionar las features
bash add_to_dvc.sh data/processed/student_performance_features.csv data-v1.2-features "Features with PCA"

dvc push
git push --tags

# ============================================================================
# ✅ COMPLETADO - Tienes 3 versiones de datos versionadas
# ============================================================================
git tag -l "data-*"
# Salida esperada:
# data-v1.0-raw
# data-v1.1-cleaned
# data-v1.2-features
```

---

## 🔧 Opciones de Remote

El script te permite elegir entre:

### Opción 1: Local (Desarrollo)
```
✅ Bueno para: Desarrollo individual
✅ Ventaja: Simple, rápido, no necesita internet
❌ Limitación: No sincroniza con el equipo
```

El script crea automáticamente: `~/dvc-storage/equipo36mlops/`

### Opción 2: Google Drive (Colaboración)
```
✅ Bueno para: Trabajo en equipo
✅ Ventaja: Sincronización entre miembros
✅ Gratis: 15GB con cuenta gratuita
⚠️  Necesita: ID de carpeta de Google Drive
```

**Cómo obtener el ID:**
1. Crea una carpeta en Google Drive
2. Abre la carpeta
3. Copia el ID de la URL: `https://drive.google.com/drive/folders/ESTE_ES_EL_ID`

### Opción 3: Skip
```
Si ya tienes remote configurado o prefieres configurarlo manualmente después.
```

---

## 📊 Estructura de Tags Recomendada

```bash
# Formato: data-v[VERSION]-[DESCRIPCION]

# Tags del proyecto equipo36mlops
data-v1.0-raw          # Dataset original en data/raw/
data-v1.1-cleaned      # Limpieza EDA aplicada
data-v1.2-features     # Features con PCA listas para ML

# Otros ejemplos útiles
data-v1.3-balanced     # Dataset balanceado
data-v1.4-augmented    # Data augmentation aplicada
data-v2.0-retrained    # Con nuevos datos
```

---

## 🛠️ Comandos Útiles Post-Setup

### Ver archivos versionados
```bash
dvc list . data/raw
dvc list . data/processed
```

### Ver estado
```bash
dvc status
```

### Ver diferencias
```bash
dvc diff
```

### Cambiar entre versiones
```bash
# Ir a versión específica
git checkout data-v1.0-original
dvc checkout

# Volver a la última
git checkout main
dvc checkout
```

### Sincronizar con equipo
```bash
# Tu compañero clona el repo
git clone <url-del-repo>
cd equipo36mlops

# Descarga los datos
dvc pull

# Ya tiene todos los datos en las versiones correctas

# Para subir cambios (tú)
dvc push
git push --tags
```

### Ver el pipeline completo
```bash
# Ver todas las versiones
git tag -l "data-*"

# Ver archivos versionados con DVC
find . -name "*.dvc"

# Ver archivos rastreados
dvc list . data/raw
dvc list . data/processed
```

---

## ❓ FAQ

### ¿Puedo versionar archivos que NO están en `data/`?
Sí, el script acepta cualquier ruta. Ejemplo:
```bash
bash setup_dvc.sh models/trained_model.pkl
bash setup_dvc.sh reports/results.csv
```

### ¿Qué pasa si ejecuto el script en el mismo archivo dos veces?
DVC detectará que el archivo ya está versionado y actualizará el tracking si el contenido cambió.

### ¿Cómo versiono cambios a un archivo ya rastreado?
Simplemente modifica el archivo y ejecuta:
```bash
dvc add data/raw/tu_archivo.csv
git add data/raw/tu_archivo.csv.dvc
git commit -m "feat: update dataset"
git tag -a "data-v1.1" -m "Updated data"
dvc push
```

### ¿Puedo usar el script con archivos grandes (GB)?
¡Sí! DVC está diseñado para archivos grandes. Solo asegúrate de tener espacio suficiente en tu remote.

### ¿Debo versionar archivos en `raw/` o `processed/`?
**Recomendación:**
- ✅ Versiona en `raw/` si es un dataset fuente/original
- ✅ Versiona en `processed/` si es resultado de transformaciones
- ✅ Puedes versionar en ambos si necesitas ambos

---

## 🎓 Mejores Prácticas

1. **Dataset Original**: Siempre versiona el dataset original primero
2. **Tags Descriptivos**: Usa tags que describan qué cambios se hicieron
3. **Commits Claros**: Mensajes de commit descriptivos
4. **Remote Configurado**: Siempre configura un remote para no perder datos
5. **Push Regular**: Haz `dvc push` después de cada cambio importante

---

## 🚨 Solución de Problemas

### Error: "dvc: command not found"
```bash
pip install dvc
```

### Error: "No se encontró el directorio .dvc"
```bash
# Inicializa DVC primero
dvc init
```

### Error: "El archivo no existe"
Verifica la ruta:
```bash
ls -la data/raw/
```

### El script no encuentra archivos CSV
Verifica que existan:
```bash
find data -name "*.csv"
```

---

## 🎯 Ejemplo Real con tu Archivo

Tu archivo actual: `data/raw/student_entry_performance.csv`

```bash
# 1. Primera vez - Versionar el archivo original
bash setup_dvc.sh data/raw/student_entry_performance.csv

# El script te pregunta:
# Remote: 1 (local)
# Tag: data-v1.0-raw
# Descripción: Raw dataset from source

# 2. Subir
dvc push
git push --tags

# 3. Ejecutar notebook EDA
jupyter notebook notebooks/1.0-el-EDA_cleaning.ipynb

# 4. Versionar resultado
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned "Clean"

# 5. Ejecutar notebook preprocessing
jupyter notebook notebooks/Preprocesamieto\ de\ Datos.ipynb

# 6. Versionar features
bash add_to_dvc.sh data/processed/student_performance_features.csv data-v1.2-features "Features"

# 7. Subir todo
dvc push
git push --tags
```

**Resultado final:**
- 3 versiones versionadas
- Pipeline reproducible
- Equipo puede sincronizar con `dvc pull`

---

## 📚 Referencias

- `DVC_WORKFLOW.md` - Flujo completo de trabajo actualizado
- `RESUMEN_FINAL.md` - Tu guía específica
- `add_to_dvc.sh` - Script para agregar archivos
- [Documentación oficial DVC](https://dvc.org/doc)

