#!/bin/bash
# ==============================================================================
# Script: add_to_dvc.sh
# Descripción: Script helper para versionar archivos y directorios con DVC
# Uso: bash add_to_dvc.sh <archivo o directorio> <tag> <mensaje>
# ==============================================================================

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Banner
echo "======================================================================"
echo "   📦 DVC Data Versioning Helper - Equipo 36 MLOps"
echo "======================================================================"
echo ""

# Validar argumentos
if [ $# -lt 3 ]; then
    print_error "Uso incorrecto del script"
    echo ""
    echo "Uso: bash add_to_dvc.sh <archivo o directorio> <tag> <mensaje>"
    echo ""
    echo "Ejemplos:"
    echo "  bash add_to_dvc.sh data/processed/student_performance.csv data-v1.1-cleaned 'Dataset after EDA cleaning'"
    echo "  bash add_to_dvc.sh data/mlflow models-v1.0-baseline 'Baseline models trained'"
    echo "  bash add_to_dvc.sh models artifacts-v1.0 'Preprocessing artifacts'"
    echo ""
    exit 1
fi

FILE_PATH=$1
TAG_NAME=$2
TAG_MESSAGE=$3

# Validar que el archivo o directorio existe
if [ ! -e "$FILE_PATH" ]; then
    print_error "El archivo o directorio '$FILE_PATH' no existe"
    exit 1
fi

if [ -d "$FILE_PATH" ]; then
    print_info "Directorio a versionar: $FILE_PATH"
else
    print_info "Archivo a versionar: $FILE_PATH"
fi
print_info "Tag: $TAG_NAME"
print_info "Mensaje: $TAG_MESSAGE"
echo ""

# Paso 1: Verificar si el archivo/directorio ya está trackeado por DVC
echo "----------------------------------------------------------------------"
print_info "PASO 1: Verificando estado..."
echo "----------------------------------------------------------------------"

if [ -f "${FILE_PATH}.dvc" ]; then
    print_warning "Ya está versionado con DVC"
    print_info "Se actualizará la versión existente"
    dvc add "$FILE_PATH"
    print_success "Actualizado en DVC"
else
    print_info "Agregando a DVC..."
    dvc add "$FILE_PATH"
    print_success "Agregado a DVC"
fi
echo ""

# Paso 2: Agregar archivo .dvc a Git
echo "----------------------------------------------------------------------"
print_info "PASO 2: Agregando metadatos DVC a Git..."
echo "----------------------------------------------------------------------"

git add "${FILE_PATH}.dvc" .gitignore
print_success "Metadatos agregados a Git"
echo ""

# Paso 3: Commit
echo "----------------------------------------------------------------------"
print_info "PASO 3: Creando commit..."
echo "----------------------------------------------------------------------"

COMMIT_MSG="feat: version data - $TAG_MESSAGE"
git commit -m "$COMMIT_MSG" || {
    print_warning "No hay cambios para commitear o el commit falló"
    print_info "Continuando con el proceso..."
}
echo ""

# Paso 4: Crear tag
echo "----------------------------------------------------------------------"
print_info "PASO 4: Creando tag Git..."
echo "----------------------------------------------------------------------"

# Verificar si el tag ya existe
if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
    print_warning "El tag '$TAG_NAME' ya existe"
    read -p "¿Deseas sobrescribirlo? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d "$TAG_NAME"
        git tag -a "$TAG_NAME" -m "$TAG_MESSAGE"
        print_success "Tag actualizado: $TAG_NAME"
    else
        print_info "Tag no actualizado"
    fi
else
    git tag -a "$TAG_NAME" -m "$TAG_MESSAGE"
    print_success "Tag creado: $TAG_NAME"
fi
echo ""

# Paso 5: Push a DVC remote (S3)
echo "----------------------------------------------------------------------"
print_info "PASO 5: Subiendo datos a DVC remote (S3)..."
echo "----------------------------------------------------------------------"

dvc push
print_success "Datos subidos a S3"
echo ""

# Paso 6: Push a Git remote
echo "----------------------------------------------------------------------"
print_info "PASO 6: Subiendo metadatos y tags a Git remote..."
echo "----------------------------------------------------------------------"

git push origin "$(git rev-parse --abbrev-ref HEAD)" || {
    print_warning "Push a origin falló - puede que no tengas permisos o no haya remote configurado"
}

git push origin "$TAG_NAME" || {
    print_warning "Push del tag falló - puede que el tag ya exista en remoto"
}
echo ""

# Resumen final
echo "======================================================================"
print_success "VERSIONADO COMPLETADO"
echo "======================================================================"
echo ""
print_info "Resumen:"
if [ -d "$FILE_PATH" ]; then
    echo "  📁 Directorio:  $FILE_PATH"
else
    echo "  📁 Archivo:     $FILE_PATH"
fi
echo "  🏷️  Tag:         $TAG_NAME"
echo "  📝 Descripción: $TAG_MESSAGE"
echo ""
print_info "Para recuperar esta versión en el futuro:"
echo "  git checkout $TAG_NAME"
echo "  dvc checkout"
echo ""
print_success "¡Listo! Tus datos están versionados correctamente."
echo "======================================================================"

