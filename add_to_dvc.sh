#!/bin/bash

# ============================================================================
# Script Auxiliar: Agregar Archivo a DVC (sin setup completo)
# ============================================================================
# Este script es para agregar rápidamente archivos a DVC cuando ya tienes
# DVC configurado y solo quieres versionar un archivo adicional.
#
# Uso: 
#   bash add_to_dvc.sh <archivo> [tag] [descripcion]
#
# Ejemplos:
#   bash add_to_dvc.sh data/processed/clean.csv
#   bash add_to_dvc.sh data/raw/new_data.csv data-v2.0 "New dataset version"
# ============================================================================

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ============================================================================
# Validar argumentos
# ============================================================================
if [ $# -lt 1 ]; then
    echo -e "${RED}❌ Error: Debes especificar un archivo${NC}"
    echo ""
    echo "Uso: bash add_to_dvc.sh <archivo> [tag] [descripcion]"
    echo ""
    echo "Ejemplos:"
    echo "  bash add_to_dvc.sh data/processed/clean.csv"
    echo "  bash add_to_dvc.sh data/raw/new_data.csv data-v2.0 \"New version\""
    exit 1
fi

TARGET_FILE="$1"
TAG_NAME="$2"
TAG_DESC="$3"

# ============================================================================
# Validar que el archivo existe
# ============================================================================
if [ ! -f "$TARGET_FILE" ]; then
    echo -e "${RED}❌ Error: El archivo no existe: $TARGET_FILE${NC}"
    exit 1
fi

# ============================================================================
# Verificar que DVC está inicializado
# ============================================================================
if [ ! -d ".dvc" ]; then
    echo -e "${RED}❌ Error: DVC no está inicializado en este proyecto${NC}"
    echo "Ejecuta primero: bash setup_dvc.sh"
    exit 1
fi

echo "============================================================================"
echo "📦 Agregando archivo a DVC"
echo "============================================================================"
echo ""

# ============================================================================
# Información del archivo
# ============================================================================
FILENAME=$(basename "$TARGET_FILE")
FILESIZE=$(du -h "$TARGET_FILE" | cut -f1)
FILELINES=$(wc -l < "$TARGET_FILE" 2>/dev/null || echo "N/A")

echo -e "${BLUE}📂 Archivo:${NC} $TARGET_FILE"
echo -e "${BLUE}📊 Tamaño:${NC} $FILESIZE"
if [ "$FILELINES" != "N/A" ]; then
    echo -e "${BLUE}📋 Líneas:${NC} $FILELINES"
fi
echo ""

# ============================================================================
# Agregar a DVC
# ============================================================================
echo -e "${BLUE}[1/3]${NC} Agregando a DVC..."
dvc add "$TARGET_FILE"
echo -e "${GREEN}✅ Archivo agregado a DVC${NC}"
echo ""

# ============================================================================
# Commit a Git
# ============================================================================
echo -e "${BLUE}[2/3]${NC} Commiteando a Git..."

TARGET_DIR=$(dirname "$TARGET_FILE")
GITIGNORE_FILE="${TARGET_DIR}/.gitignore"

if [ -f "$GITIGNORE_FILE" ]; then
    git add "${TARGET_FILE}.dvc" "$GITIGNORE_FILE"
else
    git add "${TARGET_FILE}.dvc"
fi

git commit -m "feat: add/update dataset in DVC - ${FILENAME}"
echo -e "${GREEN}✅ Cambios commiteados${NC}"
echo ""

# ============================================================================
# Crear tag (opcional)
# ============================================================================
echo -e "${BLUE}[3/3]${NC} Creando tag..."

if [ -n "$TAG_NAME" ]; then
    # Tag proporcionado como argumento
    if [ -n "$TAG_DESC" ]; then
        git tag -a "$TAG_NAME" -m "$TAG_DESC"
    else
        git tag -a "$TAG_NAME" -m "Dataset: ${FILENAME}"
    fi
    echo -e "${GREEN}✅ Tag creado: $TAG_NAME${NC}"
else
    # Preguntar si desea crear tag
    read -p "¿Deseas crear un tag de versión? (s/n) [n]: " create_tag
    create_tag=${create_tag:-n}
    
    if [[ "$create_tag" =~ ^[sS]$ ]]; then
        read -p "Ingresa el nombre del tag (ej: data-v1.0): " tag_input
        if [ -n "$tag_input" ]; then
            read -p "Descripción [Dataset: $FILENAME]: " desc_input
            desc_input=${desc_input:-"Dataset: $FILENAME"}
            git tag -a "$tag_input" -m "$desc_input"
            echo -e "${GREEN}✅ Tag creado: $tag_input${NC}"
            TAG_NAME="$tag_input"
        fi
    fi
fi

echo ""

# ============================================================================
# Resumen
# ============================================================================
echo "============================================================================"
echo -e "${GREEN}🎉 ¡Archivo agregado exitosamente!${NC}"
echo "============================================================================"
echo ""
echo "📋 Resumen:"
echo "   - Archivo: $TARGET_FILE"
echo "   - DVC file: ${TARGET_FILE}.dvc"
if [ -n "$TAG_NAME" ]; then
    echo "   - Tag: $TAG_NAME"
fi
echo ""
echo "📦 Próximos pasos:"
echo ""
echo "1. Subir al remote de DVC:"
echo "   $ dvc push"
echo ""
echo "2. Subir a Git:"
echo "   $ git push"
if [ -n "$TAG_NAME" ]; then
    echo "   $ git push --tags"
fi
echo ""
echo "============================================================================"

