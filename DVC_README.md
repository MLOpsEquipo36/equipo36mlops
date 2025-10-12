# 📦 Documentación de Versionado con DVC

## 🎯 Inicio Rápido

¿Primera vez usando DVC en este proyecto? Sigue estos pasos:

1. **Lee primero**: [`EJEMPLO_USO_DVC.md`](EJEMPLO_USO_DVC.md) - Ver ejemplo con tus datos
2. **Ejecuta**: `bash setup_dvc.sh` - Configurar y versionar
3. **Consulta**: [`QUICKSTART_DVC.md`](QUICKSTART_DVC.md) - Comandos básicos

---

## 📚 Guías Disponibles

### 🌟 Para Empezar (Orden Recomendado)

| # | Archivo | Descripción | Tiempo |
|---|---------|-------------|---------|
| 1 | [`EJEMPLO_USO_DVC.md`](EJEMPLO_USO_DVC.md) | ⭐ **Empieza aquí** - Ejemplo práctico con tus datasets | 10 min |
| 2 | [`QUICKSTART_DVC.md`](QUICKSTART_DVC.md) | Guía rápida de comandos y setup | 5 min |
| 3 | [`GUIA_SETUP_DVC.md`](GUIA_SETUP_DVC.md) | Uso detallado del script `setup_dvc.sh` | 15 min |

### 📖 Para Profundizar

| Archivo | Descripción | Tiempo |
|---------|-------------|---------|
| [`DVC_WORKFLOW.md`](DVC_WORKFLOW.md) | Flujo completo y conceptos de DVC | 20 min |
| [`CAMBIOS_DVC.md`](CAMBIOS_DVC.md) | Qué cambió en el proyecto | 5 min |

---

## 🛠️ Scripts Disponibles

### 1. `setup_dvc.sh` - Configuración Completa

**Propósito**: Primera configuración de DVC + versionar archivo

**Usos:**
```bash
# Modo interactivo (te muestra opciones)
bash setup_dvc.sh

# Modo directo (especificas el archivo)
bash setup_dvc.sh data/raw/tu_archivo.csv
```

**Cuándo usar**: Primera vez configurando DVC o agregando primer archivo

📖 [Ver guía completa](GUIA_SETUP_DVC.md)

---

### 2. `add_to_dvc.sh` - Agregar Archivo Rápido

**Propósito**: Versionar archivos cuando DVC ya está configurado

**Usos:**
```bash
# Básico
bash add_to_dvc.sh data/processed/archivo.csv

# Con tag
bash add_to_dvc.sh data/processed/archivo.csv data-v1.1

# Con tag y descripción
bash add_to_dvc.sh data/processed/archivo.csv data-v1.1 "Dataset limpio"
```

**Cuándo usar**: Ya tienes DVC configurado y solo quieres versionar un archivo nuevo/actualizado

---

## 📋 Flujo de Trabajo Típico

### Primera Vez (Setup)

```bash
# 1. Configurar DVC y versionar primer dataset
bash setup_dvc.sh data/raw/student_entry_performance_original.csv

# 2. Configurar remote (el script te pregunta)
# Elige opción 1 (local) o 2 (Google Drive)

# 3. Subir datos
dvc push
```

### Trabajo Diario

```bash
# 1. Descargar última versión
git pull
dvc pull

# 2. Trabajar en notebooks
jupyter notebook notebooks/1.0-el-EDA_cleaning.ipynb

# 3. Versionar cambios
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.2 "Cleaned data"

# 4. Subir cambios
dvc push
git push --tags
```

### Recuperar Versión Anterior

```bash
# 1. Ver versiones disponibles
git tag -l "data-*"

# 2. Cambiar a versión específica
git checkout data-v1.0-original
dvc checkout

# 3. Volver a última versión
git checkout main
dvc checkout
```

---

## 🎯 Casos de Uso Comunes

### Caso 1: Quiero versionar un archivo en `data/raw/`
```bash
bash setup_dvc.sh data/raw/mi_dataset_raw.csv
```

### Caso 2: Quiero versionar un archivo en `data/processed/`
```bash
bash setup_dvc.sh data/processed/mi_dataset_procesado.csv
```

### Caso 3: Ya tengo DVC configurado, solo quiero agregar otro archivo
```bash
bash add_to_dvc.sh data/raw/nuevo_dataset.csv
```

### Caso 4: Actualicé un archivo ya versionado
```bash
# DVC detecta el cambio automáticamente
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.3
```

### Caso 5: Quiero ver qué versión tengo actualmente
```bash
dvc status
git describe --tags
```

---

## 🗂️ Estructura Recomendada

### Versionado de Archivos

```
data/
├── raw/                              # Versionar archivos originales
│   ├── dataset_original.csv         → Versionar con setup_dvc.sh
│   └── dataset_original.csv.dvc     ← Creado por DVC
│
├── processed/                        # Versionar datasets procesados
│   ├── dataset_clean.csv            → Versionar con add_to_dvc.sh
│   ├── dataset_clean.csv.dvc        ← Creado por DVC
│   ├── dataset_features.csv         → Versionar con add_to_dvc.sh
│   └── dataset_features.csv.dvc     ← Creado por DVC
│
└── interim/                          # (Opcional) datasets intermedios
    └── dataset_temp.csv             → Versionar si es importante
```

### Tags Recomendados

```bash
data-v1.0-original      # Dataset original sin modificar
data-v1.1-cleaned       # Después de limpieza
data-v1.2-normalized    # Después de normalización
data-v2.0-features      # Con feature engineering
data-v2.1-pca           # Con PCA aplicado
data-v3.0-final         # Listo para entrenamiento
```

---

## 🚨 Comandos Importantes

### Ver Estado
```bash
dvc status                    # Estado de archivos DVC
git status                    # Estado de archivos Git
dvc diff                      # Diferencias en datos
```

### Sincronización
```bash
dvc pull                      # Descargar datos del remote
dvc push                      # Subir datos al remote
git pull                      # Descargar cambios de código
git push --tags               # Subir tags de versión
```

### Información
```bash
dvc list . data/raw          # Listar archivos en remote
git tag -l "data-*"          # Ver todas las versiones
git log --oneline            # Ver historial de commits
```

### Limpieza
```bash
dvc gc                       # Limpiar archivos no usados en remote
dvc cache clear              # Limpiar cache local
```

---

## ❓ FAQ Rápido

### ¿Qué archivo uso para versionar?
- **Primera vez**: `setup_dvc.sh`
- **Ya configurado**: `add_to_dvc.sh`

### ¿Puedo versionar archivos fuera de data/?
Sí, los scripts aceptan cualquier ruta:
```bash
bash setup_dvc.sh models/trained_model.pkl
bash add_to_dvc.sh reports/results.csv
```

### ¿Cómo sé si un archivo ya está versionado?
```bash
ls -la data/raw/*.dvc        # Ver archivos .dvc
dvc list . data/raw          # Listar en remote
```

### ¿Puedo versionar archivos grandes?
¡Sí! DVC está diseñado para eso. Incluso archivos de varios GB.

### ¿Qué pasa si no configuro un remote?
Los datos solo estarán en tu computadora. Si pierdes el caché local, pierdes los datos históricos.

### ¿Cómo colaboro con mi equipo?
1. Tu equipo clona el repo
2. Ejecutan `dvc pull`
3. Ya tienen todos los datos versionados

---

## 📞 ¿Necesitas Ayuda?

### Problemas con Scripts
Ver [`GUIA_SETUP_DVC.md`](GUIA_SETUP_DVC.md) - Sección "Solución de Problemas"

### Entender Conceptos
Ver [`DVC_WORKFLOW.md`](DVC_WORKFLOW.md) - Explicaciones detalladas

### Ver Ejemplos Prácticos
Ver [`EJEMPLO_USO_DVC.md`](EJEMPLO_USO_DVC.md) - Casos de uso reales

### Documentación Oficial
- [DVC Documentation](https://dvc.org/doc)
- [DVC Tutorials](https://dvc.org/doc/start)

---

## 🎓 Recursos de Aprendizaje

### Nivel Principiante
1. Lee: [`EJEMPLO_USO_DVC.md`](EJEMPLO_USO_DVC.md)
2. Ejecuta: `bash setup_dvc.sh`
3. Practica: Versiona 2-3 archivos diferentes

### Nivel Intermedio
1. Lee: [`DVC_WORKFLOW.md`](DVC_WORKFLOW.md)
2. Configura: Google Drive como remote
3. Practica: Cambia entre versiones con `git checkout` + `dvc checkout`

### Nivel Avanzado
1. Crea pipelines con `dvc.yaml`
2. Usa `dvc repro` para reproducibilidad
3. Integra con CI/CD

---

## ✅ Checklist de Configuración

Verifica que completaste estos pasos:

- [ ] Ejecuté `bash setup_dvc.sh` al menos una vez
- [ ] Configuré un remote (local o Google Drive)
- [ ] Hice `dvc push` exitosamente
- [ ] Verifiqué que existen archivos `.dvc` en mi proyecto
- [ ] Creé al menos un tag de versión (`data-v1.0-*`)
- [ ] Actualicé mis notebooks para usar los nombres correctos
- [ ] Mi equipo puede hacer `dvc pull` y obtener los datos
- [ ] Entiendo cómo cambiar entre versiones

---

## 📦 Resumen de Archivos

```
Documentación DVC:
├── DVC_README.md (este archivo)        ← Índice general
├── EJEMPLO_USO_DVC.md                  ← Ejemplo práctico ⭐
├── QUICKSTART_DVC.md                   ← Comandos rápidos ⭐
├── GUIA_SETUP_DVC.md                   ← Guía de scripts ⭐
├── DVC_WORKFLOW.md                     ← Conceptos completos
└── CAMBIOS_DVC.md                      ← Log de cambios

Scripts:
├── setup_dvc.sh                        ← Setup + versionar
└── add_to_dvc.sh                       ← Agregar rápido

Notebooks actualizados:
├── notebooks/1.0-el-EDA_cleaning.ipynb
└── notebooks/Preprocesamieto de Datos.ipynb
```

---

**¿Listo para empezar?** → Abre [`EJEMPLO_USO_DVC.md`](EJEMPLO_USO_DVC.md) 🚀

