#!/bin/bash

# ============================================================================
# Script para Limpiar Configuración de DVC
# ============================================================================
# Este script elimina toda la configuración de DVC para poder empezar de cero
#
# Uso: bash cleanup_dvc.sh
# ============================================================================

set -e  # Salir si hay algún error

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "============================================================================"
echo "🧹 Limpieza de Configuración de DVC"
echo "============================================================================"
echo ""

# ============================================================================
# Paso 1: Verificar estado actual
# ============================================================================
echo -e "${BLUE}[1/5]${NC} Verificando estado actual..."
echo ""

# Mostrar archivos DVC eliminados
echo "Archivos DVC eliminados detectados:"
git status --short | grep "^.D" | grep -E "(\.dvc/|\.dvcignore|\.dvc\.)" || echo "  Ninguno"
echo ""

# Mostrar tags existentes
echo "Tags existentes relacionados con datos:"
git tag | grep -E "^data-" || echo "  Ninguno"
echo ""

# ============================================================================
# Paso 2: Restaurar archivos eliminados
# ============================================================================
echo -e "${BLUE}[2/5]${NC} Restaurando archivos DVC al estado anterior..."

# Restaurar archivos .dvc que fueron eliminados
if git status --short | grep -q "^.D"; then
    echo "Restaurando archivos eliminados..."
    git restore .dvc/ 2>/dev/null || true
    git restore .dvcignore 2>/dev/null || true
    git restore data/raw/.gitignore 2>/dev/null || true
    git restore data/raw/*.dvc 2>/dev/null || true
    git restore DVC_*.md 2>/dev/null || true
    git restore README_DVC.md 2>/dev/null || true
    git restore add_to_dvc.sh 2>/dev/null || true
    echo -e "${GREEN}✅ Archivos restaurados${NC}"
else
    echo -e "${YELLOW}⚠️  No hay archivos eliminados que restaurar${NC}"
fi

echo ""

# ============================================================================
# Paso 3: Revertir commits de DVC no deseados
# ============================================================================
echo -e "${BLUE}[3/5]${NC} Limpiando commits duplicados..."
echo ""

# Contar commits con "add dataset to DVC tracking"
DUPLICATE_COMMITS=$(git log --oneline -10 | grep -c "add dataset to DVC tracking" || echo "0")

if [ "$DUPLICATE_COMMITS" -gt 1 ]; then
    echo "Se encontraron $DUPLICATE_COMMITS commits duplicados de DVC"
    echo ""
    echo "Opciones:"
    echo "  1) Hacer un soft reset (mantiene cambios en staging)"
    echo "  2) Hacer un mixed reset (mantiene cambios sin staging)"
    echo "  3) Hacer un hard reset (elimina todos los cambios) ⚠️"
    echo "  4) Dejar los commits como están"
    echo ""
    
    read -p "Selecciona una opción [1-4]: " reset_option
    
    case $reset_option in
        1)
            # Reset a antes del primer commit de DVC tracking
            COMMITS_TO_REVERT=$((DUPLICATE_COMMITS))
            git reset --soft HEAD~${COMMITS_TO_REVERT}
            echo -e "${GREEN}✅ Soft reset completado (cambios en staging)${NC}"
            ;;
        2)
            # Reset mixed
            COMMITS_TO_REVERT=$((DUPLICATE_COMMITS))
            git reset --mixed HEAD~${COMMITS_TO_REVERT}
            echo -e "${GREEN}✅ Mixed reset completado (cambios sin staging)${NC}"
            ;;
        3)
            # Hard reset - pedir confirmación
            echo -e "${RED}⚠️  ADVERTENCIA: Esto eliminará TODOS los cambios${NC}"
            read -p "¿Estás seguro? (escribe 'SI' para confirmar): " confirm
            
            if [ "$confirm" = "SI" ]; then
                COMMITS_TO_REVERT=$((DUPLICATE_COMMITS))
                git reset --hard HEAD~${COMMITS_TO_REVERT}
                echo -e "${GREEN}✅ Hard reset completado${NC}"
            else
                echo -e "${YELLOW}⚠️  Hard reset cancelado${NC}"
            fi
            ;;
        4)
            echo -e "${YELLOW}⚠️  Commits dejados sin cambios${NC}"
            ;;
        *)
            echo -e "${RED}❌ Opción inválida${NC}"
            ;;
    esac
else
    echo -e "${YELLOW}⚠️  No se encontraron commits duplicados${NC}"
fi

echo ""

# ============================================================================
# Paso 4: Eliminar tags duplicados
# ============================================================================
echo -e "${BLUE}[4/5]${NC} Limpiando tags duplicados..."
echo ""

EXISTING_TAGS=$(git tag | grep -E "^data-" || echo "")

if [ -n "$EXISTING_TAGS" ]; then
    echo "Tags encontrados:"
    echo "$EXISTING_TAGS"
    echo ""
    
    read -p "¿Deseas eliminar estos tags? (s/n) [s]: " delete_tags
    delete_tags=${delete_tags:-s}
    
    if [[ "$delete_tags" =~ ^[sS]$ ]]; then
        echo "$EXISTING_TAGS" | while read -r tag; do
            if [ -n "$tag" ]; then
                git tag -d "$tag"
                echo "  ✓ Tag eliminado: $tag"
            fi
        done
        echo -e "${GREEN}✅ Tags eliminados${NC}"
    else
        echo -e "${YELLOW}⚠️  Tags no eliminados${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No se encontraron tags de datos${NC}"
fi

echo ""

# ============================================================================
# Paso 5: Limpiar configuración de DVC (opcional)
# ============================================================================
echo -e "${BLUE}[5/5]${NC} Limpiando configuración de DVC..."
echo ""

read -p "¿Deseas eliminar completamente el directorio .dvc para empezar de cero? (s/n) [n]: " remove_dvc
remove_dvc=${remove_dvc:-n}

if [[ "$remove_dvc" =~ ^[sS]$ ]]; then
    if [ -d ".dvc" ]; then
        echo "Eliminando directorio .dvc..."
        rm -rf .dvc
        echo "Eliminando .dvcignore..."
        rm -f .dvcignore
        echo "Eliminando archivos .dvc de datasets..."
        find data -name "*.dvc" -type f -delete
        echo "Eliminando .gitignore generados por DVC..."
        find data -name ".gitignore" -type f -delete
        
        echo -e "${GREEN}✅ Configuración de DVC eliminada completamente${NC}"
        echo ""
        echo "Para reinicializar DVC, ejecuta:"
        echo "  dvc init"
    else
        echo -e "${YELLOW}⚠️  Directorio .dvc no existe${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Configuración de DVC mantenida${NC}"
    echo ""
    echo "Si deseas limpiar solo los remotes configurados:"
    echo "  dvc remote list"
    echo "  dvc remote remove <nombre_remote>"
fi

echo ""

# ============================================================================
# Finalización
# ============================================================================
echo "============================================================================"
echo -e "${GREEN}🎉 Limpieza completada${NC}"
echo "============================================================================"
echo ""
echo "📋 Estado actual:"
echo ""
git status --short

echo ""
echo "📦 Próximos pasos:"
echo ""
echo "1. Verificar que todo está limpio:"
echo "   $ git status"
echo ""
echo "2. Si eliminaste .dvc/, reinicializar DVC:"
echo "   $ dvc init"
echo ""
echo "3. Ejecutar setup_dvc.sh para configurar todo nuevamente:"
echo "   $ bash setup_dvc.sh"
echo ""
echo "============================================================================"

