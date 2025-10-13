#!/bin/bash

# ============================================================================
# Script de Configuración Inicial de DVC
# ============================================================================
# Este script configura DVC para el proyecto equipo36mlops y prepara
# datasets para versionado. Soporta múltiples tipos de remote storage:
# - Local (desarrollo)
# - Google Drive (colaboración)
# - AWS S3 (producción)
#
# Uso: 
#   bash setup_dvc.sh                              # Modo interactivo
#   bash setup_dvc.sh <ruta_archivo>               # Versionar archivo específico
#   bash setup_dvc.sh data/raw/mi_dataset.csv      # Ejemplo
# ============================================================================

set -e  # Salir si hay algún error

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================================================
# Función para mostrar uso
# ============================================================================
show_usage() {
    echo "Uso: bash setup_dvc.sh [ARCHIVO]"
    echo ""
    echo "Argumentos:"
    echo "  ARCHIVO    Ruta del dataset a versionar (opcional)"
    echo ""
    echo "Ejemplos:"
    echo "  bash setup_dvc.sh                                    # Modo interactivo"
    echo "  bash setup_dvc.sh data/raw/student_performance.csv   # Versionar archivo específico"
    echo ""
}

# ============================================================================
# Banner
# ============================================================================
echo "============================================================================"
echo "📦 Configuración Inicial de DVC para equipo36mlops"
echo "============================================================================"
echo ""

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
echo "  3) AWS S3 (recomendado para producción)"
echo "  4) Skip (configurar manualmente después)"
echo ""
read -p "Selecciona una opción [1-4]: " remote_option

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
        # Remote AWS S3
        echo ""
        echo "Para usar AWS S3, necesitas:"
        echo "  1. Un bucket S3 creado en AWS"
        echo "  2. Credenciales AWS configuradas (AWS CLI o variables de entorno)"
        echo "  3. Permisos de lectura/escritura en el bucket"
        echo ""
        read -p "Ingresa el nombre del bucket S3: " s3_bucket
        
        if [ -z "$s3_bucket" ]; then
            echo -e "${YELLOW}⚠️  Nombre de bucket no proporcionado, saltando configuración de remote${NC}"
        else
            read -p "Ingresa el path dentro del bucket (opcional, presiona Enter para usar la raíz): " s3_path
            
            # Construir la URL de S3
            if [ -z "$s3_path" ]; then
                S3_URL="s3://${s3_bucket}/equipo36mlops"
            else
                # Eliminar slashes al inicio y final del path
                s3_path=$(echo "$s3_path" | sed 's:^/*::' | sed 's:/*$::')
                S3_URL="s3://${s3_bucket}/${s3_path}"
            fi
            
            read -p "Ingresa la región de AWS (ej: us-east-1, us-west-2) [us-east-1]: " s3_region
            s3_region=${s3_region:-us-east-1}
            
            dvc remote add -d s3remote "$S3_URL" 2>/dev/null || dvc remote modify s3remote url "$S3_URL"
            dvc remote modify s3remote region "$s3_region"
            
            echo -e "${GREEN}✅ Remote AWS S3 configurado${NC}"
            echo "   - Bucket: $s3_bucket"
            echo "   - Path: $S3_URL"
            echo "   - Región: $s3_region"
            echo ""
            echo -e "${YELLOW}💡 Asegúrate de tener tus credenciales AWS configuradas:${NC}"
            echo "   - AWS CLI: aws configure"
            echo "   - Variables de entorno: AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY"
            echo "   - O credenciales de IAM role si estás en EC2/ECS"
        fi
        ;;
    4)
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
# Paso 4: Seleccionar dataset a versionar
# ============================================================================
echo -e "${BLUE}[4/6]${NC} Seleccionando dataset a versionar..."
echo ""

# Si se proporciona argumento, usar ese archivo
if [ -n "$1" ]; then
    TARGET_FILE="$1"
    echo -e "${GREEN}✅ Archivo especificado:${NC} $TARGET_FILE"
    
    if [ ! -f "$TARGET_FILE" ]; then
        echo -e "${RED}❌ Error: El archivo no existe: $TARGET_FILE${NC}"
        echo ""
        echo "Archivos disponibles en data/:"
        find data -name "*.csv" -type f 2>/dev/null | head -20
        exit 1
    fi
else
    # Modo interactivo: mostrar archivos disponibles
    echo "Archivos CSV disponibles en el proyecto:"
    echo ""
    
    # Buscar archivos CSV
    csv_files=($(find data -name "*.csv" -type f 2>/dev/null))
    
    if [ ${#csv_files[@]} -eq 0 ]; then
        echo -e "${RED}❌ No se encontraron archivos CSV en el directorio data/${NC}"
        exit 1
    fi
    
    # Mostrar lista numerada
    for i in "${!csv_files[@]}"; do
        file="${csv_files[$i]}"
        size=$(du -h "$file" | cut -f1)
        echo "  $((i+1))) $file  ($size)"
    done
    
    echo ""
    echo "  0) Ingresar ruta manualmente"
    echo ""
    
    read -p "Selecciona el archivo a versionar [1-${#csv_files[@]}] o 0: " file_choice
    
    if [ "$file_choice" = "0" ]; then
        read -p "Ingresa la ruta del archivo: " TARGET_FILE
        if [ ! -f "$TARGET_FILE" ]; then
            echo -e "${RED}❌ Error: El archivo no existe: $TARGET_FILE${NC}"
            exit 1
        fi
    elif [ "$file_choice" -ge 1 ] && [ "$file_choice" -le "${#csv_files[@]}" ]; then
        TARGET_FILE="${csv_files[$((file_choice-1))]}"
    else
        echo -e "${RED}❌ Opción inválida${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}✅ Archivo seleccionado:${NC} $TARGET_FILE"
echo -e "   Tamaño: $(du -h "$TARGET_FILE" | cut -f1)"
echo -e "   Líneas: $(wc -l < "$TARGET_FILE")"
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

# Determinar el directorio del archivo para el .gitignore
TARGET_DIR=$(dirname "$TARGET_FILE")
GITIGNORE_FILE="${TARGET_DIR}/.gitignore"

# Agregar archivos a Git
if [ -f "$GITIGNORE_FILE" ]; then
    git add "${TARGET_FILE}.dvc" "$GITIGNORE_FILE" ".dvc/config"
else
    git add "${TARGET_FILE}.dvc" ".dvc/config"
fi

# Crear mensaje de commit descriptivo
FILENAME=$(basename "$TARGET_FILE")
git commit -m "feat: add dataset to DVC tracking - ${FILENAME}"

# Crear tag de versión
echo ""
read -p "¿Deseas crear un tag de versión? (s/n) [s]: " create_tag
create_tag=${create_tag:-s}

if [[ "$create_tag" =~ ^[sS]$ ]]; then
    read -p "Ingresa el nombre del tag (ej: data-v0.1-raw): " tag_name
    if [ -z "$tag_name" ]; then
        tag_name="data-v0.1-$(date +%Y%m%d)"
        echo "Usando tag por defecto: $tag_name"
    fi
    
    read -p "Ingresa la descripción del tag: " tag_description
    if [ -z "$tag_description" ]; then
        tag_description="Dataset: ${FILENAME}"
    fi
    
    git tag -a "$tag_name" -m "$tag_description"
    echo -e "${GREEN}✅ Tag creado: $tag_name${NC}"
fi

echo -e "${GREEN}✅ Cambios commiteados exitosamente${NC}"
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
echo "   - Archivo rastreado: $TARGET_FILE"
echo "   - Archivo DVC: ${TARGET_FILE}.dvc"
echo ""
echo "📦 Próximos pasos:"
echo ""
echo "1. (Opcional) Subir los datos al remote:"
echo "   $ dvc push"
echo ""
echo "2. Subir los cambios a Git:"
echo "   $ git push"
if [[ "$create_tag" =~ ^[sS]$ ]] && [ -n "$tag_name" ]; then
    echo "   $ git push --tags"
fi
echo ""
echo "3. Para versionar otros archivos, ejecuta:"
echo "   $ bash setup_dvc.sh <ruta_del_archivo>"
echo ""
echo "4. Ver el estado de archivos versionados:"
echo "   $ dvc status"
echo ""
echo "============================================================================"
echo "💡 Ver DVC_WORKFLOW.md para el flujo completo de trabajo con DVC"
echo "============================================================================"

