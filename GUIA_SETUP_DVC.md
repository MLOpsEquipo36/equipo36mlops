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

  1) data/raw/student_entry_performance_original.csv  (52K)
  2) data/raw/student_entry_performance_modified.csv  (56K)
  3) data/processed/student_entry_performance_modified.csv  (55K)
  4) data/processed/student_entry_performance_modified_after_eda.csv  (53K)

  0) Ingresar ruta manualmente

Selecciona el archivo a versionar [1-4] o 0: _
```

---

### 2️⃣ Modo Directo (Recomendado para usuarios avanzados)

Especifica directamente el archivo que quieres versionar:

```bash
bash setup_dvc.sh <ruta_del_archivo>
```

**Ejemplos:**

#### Versionar archivo en `raw/`:
```bash
bash setup_dvc.sh data/raw/student_entry_performance_original.csv
```

#### Versionar archivo en `processed/`:
```bash
bash setup_dvc.sh data/processed/student_performance.csv
```

#### Versionar cualquier CSV:
```bash
bash setup_dvc.sh data/interim/mi_dataset_intermedio.csv
```

---

## 📋 Casos de Uso Comunes

### Caso 1: Versionar Dataset Original (Primera Vez)

```bash
# Versionar el dataset original que está en raw/
bash setup_dvc.sh data/raw/student_entry_performance_original.csv
```

**¿Qué hace?**
- ✅ Agrega el archivo a DVC (crea `.dvc` file)
- ✅ Actualiza `.gitignore` en `data/raw/`
- ✅ Hace commit a Git
- ✅ Crea tag (ej: `data-v0.1-raw`)

---

### Caso 2: Versionar Dataset Modificado

```bash
# Si ya tienes un dataset modificado que quieres versionar
bash setup_dvc.sh data/raw/student_entry_performance_modified.csv
```

---

### Caso 3: Versionar Dataset Procesado

```bash
# Después de procesar datos en un notebook
bash setup_dvc.sh data/processed/student_performance_cleaned.csv
```

---

### Caso 4: Versionar Múltiples Datasets

Ejecuta el script múltiples veces, una por cada archivo:

```bash
# Primero el original
bash setup_dvc.sh data/raw/student_entry_performance_original.csv

# Luego el modificado
bash setup_dvc.sh data/raw/student_entry_performance_modified.csv

# Y el procesado
bash setup_dvc.sh data/processed/student_performance_features.csv
```

---

## 🎨 Flujo Completo Ejemplo

### Escenario: Proyecto desde cero

```bash
# 1. Versionar dataset original en raw/
bash setup_dvc.sh data/raw/student_entry_performance_original.csv
# Tag sugerido: data-v1.0-original

# 2. Configurar remote (primera vez solamente)
# El script te preguntará: elige "1" para local o "2" para Google Drive

# 3. Subir al remote
dvc push

# 4. Hacer cambios al dataset (ejecutar notebooks, scripts, etc.)
# ... tu código transforma los datos ...

# 5. Versionar el dataset transformado
bash setup_dvc.sh data/processed/student_performance_cleaned.csv
# Tag sugerido: data-v2.0-cleaned

# 6. Subir nueva versión
dvc push
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

data-v1.0-original     # Dataset original sin modificar
data-v1.1-cleaned      # Limpieza: nulls, duplicados
data-v1.2-normalized   # Normalización de texto
data-v2.0-encoded      # Feature engineering aplicado
data-v2.1-pca          # PCA aplicado
data-v3.0-final        # Dataset listo para modelado
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
# Descargar últimas versiones
git pull
dvc pull

# Subir cambios
dvc push
git push --tags
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

## 📚 Referencias

- `DVC_WORKFLOW.md` - Flujo completo de trabajo
- `QUICKSTART_DVC.md` - Guía rápida
- `CAMBIOS_DVC.md` - Cambios realizados al proyecto
- [Documentación oficial DVC](https://dvc.org/doc)

