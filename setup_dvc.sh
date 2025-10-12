#!/bin/bash

# ============================================================================
# Script de Configuración Inicial de DVC
# ============================================================================
# Este script configura DVC para el proyecto equipo36mlops y prepara
# el dataset inicial para versionado.
#
# Uso: bash setup_dvc.sh
# ============================================================================

set -e  # Salir si hay algún error

echo "============================================================================"
echo "📦 Configuración Inicial de DVC para equipo36mlops"
echo "============================================================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# Paso 1: Verificar que DVC está instalado
# ============================================================================
echo -e "${BLUE}[1/6]${NC} Verificando instalación de DVC..."

if ! command -v dvc &> /dev/null; then
    echo -e "${YELLOW}⚠️  DVC no está instalado.${NC}"
    echo ""
    echo "Instálalo con uno de estos comandos:"
    echo "  pip install dvc"
    echo "  conda install -c conda-forge dvc"
    echo "  brew install dvc  (en macOS)"
    exit 1
fi

echo -e "${GREEN}✅ DVC está instalado:${NC} $(dvc version)"
echo ""

# ============================================================================
# Paso 2: Verificar que estamos en la raíz del proyecto
# ============================================================================
echo -e "${BLUE}[2/6]${NC} Verificando directorio del proyecto..."

if [ ! -d ".dvc" ]; then
    echo -e "${YELLOW}⚠️  No se encontró el directorio .dvc${NC}"
    echo "Este script debe ejecutarse desde la raíz del proyecto."
    exit 1
fi

echo -e "${GREEN}✅ Directorio correcto${NC}"
echo ""

# ============================================================================
# Paso 3: Configurar remote de DVC
# ============================================================================
echo -e "${BLUE}[3/6]${NC} Configurando remote de DVC..."
echo ""
echo "Opciones de remote disponibles:"
echo "  1) Local (recomendado para desarrollo)"
echo "  2) Google Drive (recomendado para colaboración)"
echo "  3) Skip (configurar manualmente después)"
echo ""
read -p "Selecciona una opción [1-3]: " remote_option

case $remote_option in
    1)
        # Remote local
        DVC_STORAGE="$HOME/dvc-storage/equipo36mlops"
        echo ""
        echo "Creando directorio de almacenamiento local: $DVC_STORAGE"
        mkdir -p "$DVC_STORAGE"
        
        dvc remote add -d local "$DVC_STORAGE" 2>/dev/null || dvc remote modify local url "$DVC_STORAGE"
        
        echo -e "${GREEN}✅ Remote local configurado${NC}"
        ;;
    2)
        # Remote Google Drive
        echo ""
        echo "Para usar Google Drive, necesitas:"
        echo "  1. Crear una carpeta en Google Drive"
        echo "  2. Obtener el ID de la carpeta (está en la URL)"
        echo ""
        read -p "Ingresa el ID de la carpeta de Google Drive: " gdrive_id
        
        if [ -z "$gdrive_id" ]; then
            echo -e "${YELLOW}⚠️  ID no proporcionado, saltando configuración de remote${NC}"
        else
            dvc remote add -d gdrive "gdrive://$gdrive_id" 2>/dev/null || dvc remote modify gdrive url "gdrive://$gdrive_id"
            dvc remote modify gdrive gdrive_acknowledge_abuse true
            
            echo -e "${GREEN}✅ Remote Google Drive configurado${NC}"
            echo -e "${YELLOW}💡 La primera vez que hagas 'dvc push' te pedirá autenticarte${NC}"
        fi
        ;;
    3)
        echo -e "${YELLOW}⚠️  Configuración de remote saltada${NC}"
        echo "Configúralo manualmente después con:"
        echo "  dvc remote add -d <nombre> <url>"
        ;;
    *)
        echo -e "${YELLOW}⚠️  Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""

# ============================================================================
# Paso 4: Preparar el dataset inicial
# ============================================================================
echo -e "${BLUE}[4/6]${NC} Preparando dataset inicial..."

SOURCE_FILE="data/raw/student_entry_performance_original.csv"
TARGET_FILE="data/processed/student_performance.csv"

if [ ! -f "$SOURCE_FILE" ]; then
    echo -e "${YELLOW}⚠️  Archivo fuente no encontrado: $SOURCE_FILE${NC}"
    echo "Asegúrate de tener el dataset original en la ubicación correcta."
    exit 1
fi

# Copiar el archivo original como base
cp "$SOURCE_FILE" "$TARGET_FILE"
echo -e "${GREEN}✅ Dataset copiado a: $TARGET_FILE${NC}"
echo ""

# ============================================================================
# Paso 5: Agregar el dataset a DVC
# ============================================================================
echo -e "${BLUE}[5/6]${NC} Agregando dataset a DVC..."

dvc add "$TARGET_FILE"

echo -e "${GREEN}✅ Dataset agregado a DVC${NC}"
echo "   - Creado: ${TARGET_FILE}.dvc"
echo "   - Actualizado: data/processed/.gitignore"
echo ""

# ============================================================================
# Paso 6: Commitear cambios a Git
# ============================================================================
echo -e "${BLUE}[6/6]${NC} Commiteando cambios a Git..."

git add "${TARGET_FILE}.dvc" "data/processed/.gitignore" ".dvc/config"
git commit -m "feat: add initial dataset version to DVC (data-v0.1-raw)"

# Crear tag
git tag -a "data-v0.1-raw" -m "Version 0.1: Raw original data"

echo -e "${GREEN}✅ Cambios commiteados y tag creado: data-v0.1-raw${NC}"
echo ""

# ============================================================================
# Finalización
# ============================================================================
echo "============================================================================"
echo -e "${GREEN}🎉 ¡Configuración completada exitosamente!${NC}"
echo "============================================================================"
echo ""
echo "📋 Resumen:"
echo "   - DVC configurado y listo"
echo "   - Dataset inicial versionado: data-v0.1-raw"
echo "   - Archivo rastreado: $TARGET_FILE"
echo ""
echo "📦 Próximos pasos:"
echo ""
echo "1. (Opcional) Subir los datos al remote:"
echo "   $ dvc push"
echo ""
echo "2. Subir los cambios a Git:"
echo "   $ git push"
echo "   $ git push --tags"
echo ""
echo "3. Ejecutar el notebook de EDA:"
echo "   notebooks/1.0-el-EDA_cleaning.ipynb"
echo ""
echo "4. Después del EDA, versionar los cambios siguiendo las instrucciones del notebook"
echo ""
echo "============================================================================"
echo "💡 Ver DVC_WORKFLOW.md para el flujo completo de trabajo con DVC"
echo "============================================================================"

