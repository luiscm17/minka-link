#!/bin/bash

set -e  # Detener el script en caso de error

# Verificar que se proporcione el nombre del grupo de recursos
if [ $# -eq 0 ]; then
    echo "Error: No se proporcionó el nombre del grupo de recursos."
    echo "Uso: $0 <nombre-del-grupo-de-recursos>"
    echo "Ejemplo: $0 rg-chatbot-1234"
    exit 1
fi

RESOURCE_GROUP="$1"

# Verificar si el grupo de recursos existe
echo "Verificando la existencia del grupo de recursos: $RESOURCE_GROUP"
if ! az group show --name "$RESOURCE_GROUP" &>/dev/null; then
    echo "Error: El grupo de recursos '$RESOURCE_GROUP' no existe o no tienes permisos para acceder a él."
    exit 1
fi

# Mostrar los recursos que serán eliminados
echo -e "\n=== Recursos que serán eliminados ==="
az resource list --resource-group "$RESOURCE_GROUP" --query "[].{Name:name, Type:type}" -o table

# Confirmación del usuario
read -p "¿Estás seguro de que deseas eliminar el grupo de recursos '$RESOURCE_GROUP' y todos sus recursos? (s/n): " -n 1 -r
echo    # Mover a una nueva línea

if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo "Eliminando el grupo de recursos: $RESOURCE_GROUP"
    az group delete --name "$RESOURCE_GROUP" --yes --no-wait
    echo "La eliminación del grupo de recursos ha comenzado. Esto puede tomar varios minutos."
    echo "Puedes verificar el estado en Azure Portal o con: az group show --name $RESOURCE_GROUP"
else
    echo "Operación cancelada. No se eliminó ningún recurso."
fi
