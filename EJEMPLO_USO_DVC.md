# 🎯 Ejemplo Práctico: Versionando tus Datasets Actuales

## 📁 Tu Situación Actual

Tienes estos archivos en `data/raw/`:
```
data/raw/
├── student_entry_performance_original.csv  (52KB)
└── student_entry_performance_modified.csv  (56KB)
```

Y en `data/processed/`:
```
data/processed/
├── student_entry_performance_modified.csv
└── student_entry_performance_modified_after_eda.csv
```

---

## 🚀 Plan de Versionado Recomendado

### Estrategia: Mantener Historial de Transformaciones

En lugar de tener múltiples archivos, vamos a crear un historial limpio:

```
Versión 1: Original (raw)
    ↓
Versión 2: Modified (primera transformación)
    ↓
Versión 3: After EDA (limpieza aplicada)
```

---

## 📝 Paso a Paso

### Paso 1: Versionar el Dataset Original 📊

Este es tu punto de partida, el dataset sin modificar.

```bash
# Versionar el archivo original
bash setup_dvc.sh data/raw/student_entry_performance_original.csv
```

**Durante el proceso:**
1. Selecciona la opción de remote (elige "1" para local)
2. Cuando pregunte por el tag: `data-v1.0-original`
3. Descripción: `Original raw dataset from source`

**Resultado:**
- ✅ Creado: `data/raw/student_entry_performance_original.csv.dvc`
- ✅ Actualizado: `data/raw/.gitignore`
- ✅ Tag: `data-v1.0-original`

```bash
# Subir al remote
dvc push
git push --tags
```

---

### Paso 2: Versionar el Dataset Modificado 📝

Este tiene las primeras modificaciones.

```bash
# Versionar el archivo modificado
bash setup_dvc.sh data/raw/student_entry_performance_modified.csv
```

**Tags sugeridos:**
- Nombre: `data-v1.1-modified`
- Descripción: `Dataset with initial modifications`

```bash
dvc push
git push --tags
```

---

### Paso 3: Consolidar el Flujo para el Futuro 🔄

Para evitar tener múltiples archivos en el futuro, vamos a usar un solo archivo que evoluciona:

```bash
# 1. Copiar el original como punto de partida
cp data/raw/student_entry_performance_original.csv data/processed/student_performance.csv

# 2. Versionarlo
bash setup_dvc.sh data/processed/student_performance.csv
# Tag: data-v2.0-base
# Descripción: Base dataset for processing pipeline
```

Ahora, cada vez que transformes los datos:

```bash
# 3. Ejecutar notebook de EDA (que modifica student_performance.csv)
jupyter notebook notebooks/1.0-el-EDA_cleaning.ipynb

# 4. Versionar los cambios
bash add_to_dvc.sh data/processed/student_performance.csv data-v2.1-cleaned "After EDA cleaning"

# 5. Ejecutar notebook de preprocessing
jupyter notebook notebooks/Preprocesamieto\ de\ Datos.ipynb

# 6. Versionar las features generadas
bash add_to_dvc.sh data/processed/student_performance_features.csv data-v2.2-features "Engineered features with PCA"
```

---

## 🎨 Flujo Visual

### Antes (❌ Confuso):
```
data/
├── raw/
│   ├── original.csv
│   └── modified.csv
└── processed/
    ├── modified.csv
    └── modified_after_eda.csv
```
*Muchos archivos con nombres similares*

### Después (✅ Claro):
```
Git History:
├── v1.0-original     → data/raw/student_entry_performance_original.csv
├── v1.1-modified     → data/raw/student_entry_performance_modified.csv
├── v2.0-base         → data/processed/student_performance.csv (original)
├── v2.1-cleaned      → data/processed/student_performance.csv (después EDA)
└── v2.2-features     → data/processed/student_performance_features.csv
```
*Un historial claro de transformaciones*

---

## 📋 Comandos Completos (Copy & Paste)

### Opción A: Versionar Todo lo que Tienes Ahora

```bash
# 1. Versionar original
bash setup_dvc.sh data/raw/student_entry_performance_original.csv
# Tag: data-v1.0-original
# Descripción: Original raw dataset

# 2. Versionar modified
bash setup_dvc.sh data/raw/student_entry_performance_modified.csv
# Tag: data-v1.1-modified  
# Descripción: Dataset with initial modifications

# 3. Versionar processed (after eda)
bash setup_dvc.sh data/processed/student_entry_performance_modified_after_eda.csv
# Tag: data-v1.2-cleaned
# Descripción: Dataset after EDA cleaning

# 4. Subir todo
dvc push
git push --tags
```

### Opción B: Empezar de Cero con Estructura Limpia (Recomendado)

```bash
# 1. Respaldar archivos actuales
mkdir -p backup_datasets
cp data/processed/*.csv backup_datasets/

# 2. Crear estructura limpia
cp data/raw/student_entry_performance_original.csv data/processed/student_performance.csv

# 3. Versionar el base
bash setup_dvc.sh data/processed/student_performance.csv
# Tag: data-v1.0-base
# Descripción: Base dataset for processing

# 4. Ejecutar notebook de EDA (modifica el archivo)
jupyter notebook notebooks/1.0-el-EDA_cleaning.ipynb

# 5. Versionar cambios
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned "After EDA"

# 6. Ejecutar preprocessing
jupyter notebook notebooks/Preprocesamieto\ de\ Datos.ipynb

# 7. Versionar features
bash add_to_dvc.sh data/processed/student_performance_features.csv data-v1.2-features "With PCA"

# 8. Subir todo
dvc push
git push --tags
```

---

## 🔍 Verificar Versionado

### Ver archivos rastreados por DVC
```bash
find . -name "*.dvc"
```

### Ver tags creados
```bash
git tag -l "data-*"
```

### Ver historial de un archivo
```bash
git log --oneline -- data/processed/student_performance.csv.dvc
```

### Ver qué versión estás usando
```bash
dvc status
git describe --tags
```

---

## 🎯 Casos de Uso Futuros

### Caso 1: Recibiste un nuevo dataset
```bash
# Copiar el nuevo archivo
cp ~/Downloads/nuevo_dataset.csv data/raw/student_data_2024.csv

# Versionarlo
bash add_to_dvc.sh data/raw/student_data_2024.csv data-v2.0-new "New 2024 dataset"

dvc push
git push --tags
```

### Caso 2: Actualizaste el EDA
```bash
# El notebook sobrescribe student_performance.csv
jupyter notebook notebooks/1.0-el-EDA_cleaning.ipynb

# Versionar cambios
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.3-eda-updated "Updated EDA with new cleaning"

dvc push
```

### Caso 3: Necesitas volver a una versión anterior
```bash
# Ver versiones disponibles
git tag -l

# Cambiar a versión específica
git checkout data-v1.0-base
dvc checkout

# Ver el archivo (ahora tiene los datos de esa versión)
head data/processed/student_performance.csv

# Volver a la última versión
git checkout main
dvc checkout
```

### Caso 4: Un compañero quiere obtener tus datos
```bash
# Tu compañero hace:
git clone <repo-url>
cd equipo36mlops
dvc pull

# ¡Y tiene todos los datos versionados!
```

---

## 💡 Tips y Mejores Prácticas

### 1. Nomenclatura de Tags
```bash
# Formato recomendado
data-v[MAJOR].[MINOR]-[STAGE]

# Ejemplos:
data-v1.0-raw         # Primera versión raw
data-v1.1-cleaned     # Limpieza minor
data-v2.0-resampled   # Cambio major (nuevo muestreo)
data-v2.1-features    # Features agregadas
```

### 2. Cuándo Crear Nueva Versión
```
✅ Crear nueva versión cuando:
- Modificaste los datos
- Agregaste/removiste columnas
- Cambiaste valores (limpieza, imputación)
- Aplicaste transformaciones

❌ NO crear versión cuando:
- Solo leíste el archivo
- Ejecutaste análisis sin modificar
- Creaste visualizaciones
```

### 3. Mantener data/raw/ Intacto
```bash
# ✅ BIEN: data/raw/ solo contiene originales sin modificar
data/raw/
└── student_entry_performance_original.csv

# ✅ BIEN: Transformaciones van a data/processed/
data/processed/
├── student_performance.csv          # Evoluciona con versiones
└── student_performance_features.csv # Resultado final
```

### 4. Usar Scripts para Actualizar
```bash
# En lugar de versionear manualmente cada vez,
# puedes agregar al final de tu notebook:

import subprocess

# Al final del notebook
subprocess.run([
    "bash", "add_to_dvc.sh", 
    "data/processed/student_performance.csv",
    f"data-v1.{version_number}-cleaned",
    "Automated versioning from notebook"
])
```

---

## 🆘 ¿Necesitas Ayuda?

### El script no encuentra mi archivo
```bash
# Verifica que existe
ls -la data/raw/student_entry_performance_original.csv

# Usa la ruta completa si es necesario
bash setup_dvc.sh $(pwd)/data/raw/student_entry_performance_original.csv
```

### Ya tengo archivos .dvc viejos
```bash
# Elimina los .dvc files viejos y empieza de nuevo
rm data/**/*.dvc
git rm --cached data/**/*.dvc

# Luego ejecuta el setup
bash setup_dvc.sh <tu_archivo>
```

### Quiero cambiar el nombre de un archivo versionado
```bash
# 1. Renombrar archivo y .dvc
mv old_name.csv new_name.csv
mv old_name.csv.dvc new_name.csv.dvc

# 2. Actualizar el .dvc file (editar la ruta dentro)
# 3. Commitear
git add new_name.csv.dvc
git rm old_name.csv.dvc
git commit -m "refactor: rename dataset"
```

---

## ✅ Checklist Final

Antes de considerar que tu versionado está completo:

- [ ] DVC inicializado (`.dvc/` existe)
- [ ] Remote configurado (`dvc remote list` muestra algo)
- [ ] Archivos importantes versionados (`.dvc` files creados)
- [ ] Tags creados para versiones importantes
- [ ] Hiciste `dvc push` al menos una vez
- [ ] `.gitignore` actualizado (archivos grandes no en Git)
- [ ] Notebooks actualizados para usar los nombres correctos
- [ ] README del proyecto documenta el flujo de datos

---

¡Listo! Ahora tienes un sistema profesional de versionado de datos. 🎉

