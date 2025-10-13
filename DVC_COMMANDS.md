# 🔧 Comandos DVC - Referencia Rápida

## 📝 Comandos Básicos

### Agregar archivos a DVC

```bash
# Agregar un archivo nuevo
dvc add data/processed/mi_archivo.csv

# Agregar un directorio completo
dvc add data/mlflow/
```

### Subir datos a S3

```bash
# Subir todos los archivos trackeados
dvc push

# Subir un archivo específico
dvc push data/processed/student_performance.csv.dvc
```

### Descargar datos de S3

```bash
# Descargar todos los archivos
dvc pull

# Descargar un archivo específico
dvc pull data/processed/student_performance.csv.dvc
```

### Sincronizar versión de datos con Git

```bash
# Actualizar archivos DVC al estado del commit actual
dvc checkout

# Actualizar un archivo específico
dvc checkout data/processed/student_performance.csv.dvc
```

---

## 🔍 Comandos de Inspección

### Ver estado de DVC

```bash
# Ver qué archivos han cambiado
dvc status

# Ver estado de un archivo específico
dvc status data/processed/student_performance.csv.dvc

# Ver qué archivos están trackeados
dvc list . -R
```

### Ver diferencias entre versiones

```bash
# Comparar el estado actual con el HEAD
dvc diff

# Comparar dos commits/tags
dvc diff data-v1.1-cleaned data-v1.2-features

# Ver diferencias en métricas (si usas dvc metrics)
dvc metrics diff
```

### Ver información de archivos

```bash
# Ver metadata de un archivo .dvc
cat data/processed/student_performance.csv.dvc

# Ver historial de cambios de un archivo
git log --oneline -- data/processed/student_performance.csv.dvc
```

---

## 🏷️ Trabajar con Tags

### Crear y gestionar tags

```bash
# Crear un tag
git tag -a "data-v1.1-cleaned" -m "Dataset after EDA cleaning"

# Listar todos los tags
git tag -l

# Ver información de un tag
git show data-v1.1-cleaned

# Eliminar un tag local
git tag -d data-v1.1-cleaned

# Eliminar un tag remoto
git push origin --delete data-v1.1-cleaned
```

### Cambiar a una versión específica

```bash
# Cambiar a un tag específico
git checkout data-v1.1-cleaned
dvc checkout

# Volver a la rama principal
git checkout main
dvc checkout
```

### Subir tags a remoto

```bash
# Subir un tag específico
git push origin data-v1.1-cleaned

# Subir todos los tags
git push origin --tags

# Forzar actualización de un tag (usar con cuidado)
git push origin data-v1.1-cleaned --force
```

---

## 🔄 Flujo Completo de Versionado

### Método rápido (usando el script)

```bash
bash add_to_dvc.sh <archivo> <tag> <mensaje>

# Ejemplo:
bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned 'Dataset after EDA cleaning'
```

### Método manual (paso a paso)

```bash
# 1. Agregar archivo a DVC
dvc add data/processed/student_performance.csv

# 2. Agregar metadatos a Git
git add data/processed/student_performance.csv.dvc .gitignore

# 3. Hacer commit
git commit -m "feat: version data - dataset after EDA cleaning"

# 4. Crear tag
git tag -a "data-v1.1-cleaned" -m "Dataset after EDA cleaning"

# 5. Subir datos a S3
dvc push

# 6. Subir código y tags a Git
git push origin main
git push origin data-v1.1-cleaned
```

---

## 🛠️ Comandos de Configuración

### Ver configuración

```bash
# Ver toda la configuración de DVC
dvc config -l

# Ver configuración de un proyecto específico
cat .dvc/config

# Ver remote storage configurado
dvc remote list
```

### Configurar remote storage (S3)

```bash
# Agregar remote storage
dvc remote add -d s3remote s3://mlops-team36-bucket/equipo36mlops

# Configurar región
dvc remote modify s3remote region us-east-2

# Ver configuración del remote
dvc remote list --show-url
```

### Configurar credenciales AWS

```bash
# Opción 1: Usar AWS CLI
aws configure

# Opción 2: Usar variables de entorno
export AWS_ACCESS_KEY_ID="tu-access-key"
export AWS_SECRET_ACCESS_KEY="tu-secret-key"
export AWS_DEFAULT_REGION="us-east-2"

# Opción 3: Usar el script del proyecto
bash setup_aws_credentials.sh
```

---

## 🧹 Comandos de Limpieza

### Limpiar cache local

```bash
# Ver espacio usado por el cache
dvc cache dir

# Limpiar archivos no usados del cache
dvc gc

# Limpiar todo el cache (usar con precaución)
dvc cache dir
rm -rf .dvc/cache/*
```

### Dejar de trackear archivos

```bash
# Remover archivo de DVC pero mantener el archivo
dvc remove data/processed/student_performance.csv.dvc

# Remover y eliminar el archivo
dvc remove data/processed/student_performance.csv.dvc --outs
```

---

## 🔧 Comandos de Troubleshooting

### Reparar cache corrupto

```bash
# Verificar integridad del cache
dvc cache dir

# Re-descargar archivos desde S3
dvc pull --force
```

### Resolver conflictos

```bash
# Si hay conflictos con archivos .dvc
git checkout --ours data/processed/student_performance.csv.dvc  # usar versión local
# o
git checkout --theirs data/processed/student_performance.csv.dvc  # usar versión remota

# Luego hacer checkout del archivo
dvc checkout data/processed/student_performance.csv.dvc
```

### Forzar re-sincronización

```bash
# Forzar push (sobrescribir en S3)
dvc push --force

# Forzar pull (sobrescribir local)
dvc pull --force

# Re-calcular hashes
dvc status --cloud
```

---

## 📊 Comandos Avanzados

### Pipelines con DVC

```bash
# Reproducir pipeline completo
dvc repro

# Ver DAG del pipeline
dvc dag

# Listar stages del pipeline
dvc stage list
```

### Métricas y experimentos

```bash
# Mostrar métricas
dvc metrics show

# Comparar métricas entre versiones
dvc metrics diff data-v1.1-cleaned data-v1.2-features

# Listar experimentos
dvc exp list

# Mostrar tabla de experimentos
dvc exp show
```

### Gestión de cache remoto

```bash
# Verificar qué archivos están en S3
dvc list -R s3://mlops-team36-bucket/equipo36mlops

# Ver estado en la nube
dvc status --cloud

# Sincronizar cache con S3
dvc fetch
```

---

## 🎯 Patrones de Uso Comunes

### Al comenzar el día

```bash
# Sincronizar todo
git pull
dvc pull

# Verificar estado
git status
dvc status
```

### Al terminar el día

```bash
# Versionar cambios en datos
bash add_to_dvc.sh <archivo> <tag> <mensaje>

# O manualmente:
dvc add <archivos-modificados>
git add .
git commit -m "descripción"
dvc push
git push
```

### Trabajar con una versión específica

```bash
# Cambiar a versión
git checkout <tag>
dvc checkout

# Hacer pruebas/experimentos
# ...

# Volver a la versión actual
git checkout main
dvc checkout
```

### Comparar dos versiones

```bash
# Método 1: Usar dvc diff
dvc diff tag1 tag2

# Método 2: Checkout manual
git checkout tag1 && dvc checkout
# Copiar archivo
cp data/processed/student_performance.csv /tmp/version1.csv

git checkout tag2 && dvc checkout
cp data/processed/student_performance.csv /tmp/version2.csv

# Comparar con herramientas externas
diff /tmp/version1.csv /tmp/version2.csv
```

---

## 🔗 Integración con Git

### Comandos combinados útiles

```bash
# Ver todos los cambios en archivos .dvc
git log --oneline --all -- **/*.dvc

# Ver cambios en un archivo específico
git log -p -- data/processed/student_performance.csv.dvc

# Encontrar en qué commit se creó un tag
git log --oneline --decorate --all | grep "data-v1.1-cleaned"

# Ver archivos trackeados por DVC en el commit actual
find . -name "*.dvc" -type f
```

---

## 📚 Recursos Adicionales

- **Documentación oficial**: https://dvc.org/doc
- **Tutorial DVC**: https://dvc.org/doc/start
- **DVC con S3**: https://dvc.org/doc/user-guide/data-management/remote-storage/amazon-s3
- **Guía del proyecto**: `docs/DVC_WORKFLOW.md`

---

**Última actualización**: Octubre 2025  
**Equipo 36 MLOps**

