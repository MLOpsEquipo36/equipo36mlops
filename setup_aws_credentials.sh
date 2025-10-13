#!/bin/bash

# ============================================================================
# Script para Configurar Credenciales de AWS
# ============================================================================
# Este script te ayuda a configurar las credenciales de AWS para usar con DVC
#
# Uso: bash setup_aws_credentials.sh
# ============================================================================

set -e  # Salir si hay algún error

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "============================================================================"
echo "🔐 Configuración de Credenciales AWS para DVC"
echo "============================================================================"
echo ""

# ============================================================================
# Verificar configuración de DVC
# ============================================================================
echo -e "${BLUE}Configuración actual de DVC:${NC}"
dvc remote list
echo ""

# ============================================================================
# Opciones de configuración
# ============================================================================
echo "Hay 3 formas de configurar las credenciales de AWS:"
echo ""
echo "  1) Instalar AWS CLI y configurar (recomendado)"
echo "  2) Variables de entorno (temporal)"
echo "  3) Configurar credenciales manualmente en archivos"
echo ""
read -p "Selecciona una opción [1-3]: " config_option

case $config_option in
    1)
        echo ""
        echo -e "${BLUE}[Opción 1] Instalación de AWS CLI${NC}"
        echo ""
        
        # Detectar sistema operativo
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "Detectado: macOS"
            echo ""
            echo "Para instalar AWS CLI, ejecuta:"
            echo ""
            echo "Opción A - Usando Homebrew (recomendado):"
            echo "  brew install awscli"
            echo ""
            echo "Opción B - Usando pip:"
            echo "  pip install awscli"
            echo ""
            echo "Opción C - Instalador oficial:"
            echo "  curl 'https://awscli.amazonaws.com/AWSCLIV2.pkg' -o 'AWSCLIV2.pkg'"
            echo "  sudo installer -pkg AWSCLIV2.pkg -target /"
            echo ""
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "Detectado: Linux"
            echo ""
            echo "Para instalar AWS CLI:"
            echo "  pip install awscli"
            echo ""
        else
            echo "Sistema: $OSTYPE"
            echo ""
            echo "Instala AWS CLI desde: https://aws.amazon.com/cli/"
            echo ""
        fi
        
        read -p "¿Ya instalaste AWS CLI? (s/n): " installed_cli
        
        if [[ "$installed_cli" =~ ^[sS]$ ]]; then
            echo ""
            echo "Ahora vamos a configurar las credenciales..."
            echo ""
            echo "Necesitarás:"
            echo "  - AWS Access Key ID"
            echo "  - AWS Secret Access Key"
            echo "  - Región (ya configurada: us-east-2)"
            echo ""
            echo "Puedes obtener estas credenciales en:"
            echo "  AWS Console -> IAM -> Users -> Security Credentials"
            echo ""
            read -p "¿Tienes las credenciales? (s/n): " has_creds
            
            if [[ "$has_creds" =~ ^[sS]$ ]]; then
                echo ""
                echo "Ejecuta este comando para configurar:"
                echo ""
                echo -e "${GREEN}aws configure${NC}"
                echo ""
                echo "Te preguntará:"
                echo "  AWS Access Key ID: [tu_access_key]"
                echo "  AWS Secret Access Key: [tu_secret_key]"
                echo "  Default region name: us-east-2"
                echo "  Default output format: json"
                echo ""
                
                read -p "Presiona Enter para ejecutar 'aws configure'..." 
                aws configure
                
                echo ""
                echo -e "${GREEN}✅ Credenciales configuradas con AWS CLI${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  Instala AWS CLI primero y luego ejecuta 'aws configure'${NC}"
        fi
        ;;
        
    2)
        echo ""
        echo -e "${BLUE}[Opción 2] Variables de Entorno (Temporal)${NC}"
        echo ""
        echo "Esta opción configura las credenciales solo para la sesión actual."
        echo ""
        
        read -p "AWS Access Key ID: " aws_access_key
        read -p "AWS Secret Access Key: " aws_secret_key
        
        if [ -n "$aws_access_key" ] && [ -n "$aws_secret_key" ]; then
            echo ""
            echo "Exportando variables de entorno..."
            export AWS_ACCESS_KEY_ID="$aws_access_key"
            export AWS_SECRET_ACCESS_KEY="$aws_secret_key"
            export AWS_DEFAULT_REGION="us-east-2"
            
            echo ""
            echo -e "${GREEN}✅ Variables de entorno configuradas${NC}"
            echo ""
            echo "Para que las variables persistan, agrega estas líneas a tu ~/.zshrc o ~/.bashrc:"
            echo ""
            echo "export AWS_ACCESS_KEY_ID='$aws_access_key'"
            echo "export AWS_SECRET_ACCESS_KEY='$aws_secret_key'"
            echo "export AWS_DEFAULT_REGION='us-east-2'"
            echo ""
            echo -e "${YELLOW}⚠️  Estas credenciales solo estarán disponibles en esta sesión${NC}"
            echo ""
            
            # Guardar en archivo temporal para uso inmediato
            cat > /tmp/aws_env_vars.sh << EOF
export AWS_ACCESS_KEY_ID='$aws_access_key'
export AWS_SECRET_ACCESS_KEY='$aws_secret_key'
export AWS_DEFAULT_REGION='us-east-2'
EOF
            
            echo "Archivo temporal creado: /tmp/aws_env_vars.sh"
            echo "Ejecuta: source /tmp/aws_env_vars.sh"
        else
            echo -e "${RED}❌ Credenciales no proporcionadas${NC}"
            exit 1
        fi
        ;;
        
    3)
        echo ""
        echo -e "${BLUE}[Opción 3] Configuración Manual${NC}"
        echo ""
        
        # Crear directorio si no existe
        mkdir -p ~/.aws
        
        read -p "AWS Access Key ID: " aws_access_key
        read -p "AWS Secret Access Key: " aws_secret_key
        
        if [ -n "$aws_access_key" ] && [ -n "$aws_secret_key" ]; then
            # Crear archivo de credenciales
            cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = $aws_access_key
aws_secret_access_key = $aws_secret_key
EOF
            
            # Crear archivo de configuración
            cat > ~/.aws/config << EOF
[default]
region = us-east-2
output = json
EOF
            
            chmod 600 ~/.aws/credentials
            chmod 600 ~/.aws/config
            
            echo ""
            echo -e "${GREEN}✅ Credenciales guardadas en ~/.aws/credentials${NC}"
            echo -e "${GREEN}✅ Configuración guardada en ~/.aws/config${NC}"
        else
            echo -e "${RED}❌ Credenciales no proporcionadas${NC}"
            exit 1
        fi
        ;;
        
    *)
        echo -e "${RED}❌ Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo "============================================================================"
echo -e "${GREEN}🎉 Configuración completada${NC}"
echo "============================================================================"
echo ""

# Verificar que las credenciales funcionan
echo "Verificando credenciales..."
echo ""

if command -v aws &> /dev/null; then
    echo "Probando conexión con AWS..."
    if aws sts get-caller-identity &> /dev/null; then
        echo -e "${GREEN}✅ Credenciales verificadas correctamente${NC}"
        aws sts get-caller-identity
    else
        echo -e "${YELLOW}⚠️  No se pudo verificar las credenciales con AWS CLI${NC}"
        echo "Pero puedes intentar hacer 'dvc push' de todas formas."
    fi
else
    echo -e "${YELLOW}⚠️  AWS CLI no disponible para verificar credenciales${NC}"
    echo "Pero las credenciales están configuradas. Intenta 'dvc push'."
fi

echo ""
echo "📦 Próximos pasos:"
echo ""
echo "1. Verificar acceso al bucket S3:"
echo "   $ aws s3 ls s3://mlops-team36-bucket/ (si tienes AWS CLI)"
echo ""
echo "2. Intentar push de DVC:"
echo "   $ dvc push"
echo ""
echo "3. Si hay problemas de permisos, verifica en AWS Console que tu usuario tenga:"
echo "   - s3:PutObject"
echo "   - s3:GetObject"
echo "   - s3:ListBucket"
echo ""
echo "============================================================================"

