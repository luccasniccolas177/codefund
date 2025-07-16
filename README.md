# CodeFund Backend - API y Agente de Verificación Autónomo

Este repositorio contiene el código fuente del backend para CodeFund, compuesto por dos servicios principales escritos en Python:

    Una API RESTful (FastAPI): Actúa como un puente eficiente entre el frontend y la blockchain. Proporciona endpoints para consultar información de campañas y usuarios de forma rápida, evitando que el frontend tenga que hacer costosas llamadas a la blockchain para cada vista.

    Un Agente de Verificación Autónomo: Un script independiente que se ejecuta en segundo plano. Su misión es monitorear la blockchain, verificar las condiciones de los hitos en GitHub y enviar transacciones para aprobarlos automáticamente.

🚀 Funcionalidades Implementadas

✅ API RESTful:

    Endpoints para listar todos los proyectos (/api/v1/projects).

    Endpoint para ver los detalles completos de un proyecto, incluyendo sus hitos (/api/v1/projects/{address}).

    Endpoints para el Dashboard de usuario: listar proyectos creados (/users/{address}/created) y contribuidos (/users/{address}/contributed).

✅ Agente de Verificación:

    Escanea periódicamente todas las campañas en la blockchain.

    Para los hitos pendientes, extrae la URL de verificación (ej. un Pull Request de GitHub).

    Usa la API de GitHub para comprobar si el PR ha sido fusionado ("merged").

    Si la condición se cumple, utiliza su propia wallet para enviar una transacción on-chain y aprobar el hito en el contrato inteligente correspondiente.

🛠️ Pila Tecnológica

    Framework API: FastAPI

    Servidor ASGI: Uvicorn

    Interacción Blockchain: Web3.py

    Cliente HTTP (Agente): Requests

    Gestión de Secretos: python-dotenv

    Lenguaje: Python 3.10+

⚙️ Instalación y Configuración
Requisitos Previos

    Python (versión 3.10 o superior)

    Una dirección de contrato CampaignFactory desplegada en Sepolia.

### 1. Clonar el repositorio y navegar a la carpeta

git clone <repo_url>
cd <nombre_del_repo>/app-backend

### 2. Crear y activar un entorno virtual

Crear el entorno
python3 -m venv venv

Activar en macOS / Linux
source venv/bin/activate

Activar en Windows
venv\Scripts\activate

### 3. Instalar dependencias

pip install fastapi "uvicorn[standard]" web3 python-dotenv requests

### 4. Configurar las variables de entorno

Este es el paso más importante para que tanto la API como el Agente puedan funcionar.

    Crea un archivo llamado .env en la raíz de la carpeta app-backend.

    Pega el siguiente contenido y rellena tus datos.

    # =================================================
    # === CONFIGURACIÓN PARA EL AGENTE (agent.py) ===
    # =================================================

    # La clave privada de una wallet de Sepolia que actuará como el agente.
    # ¡ASEGÚRATE DE QUE TENGA ETH DE SEPOLIA PARA PAGAR EL GAS!
    AGENT_PRIVATE_KEY="0x..."

    # Tu Token de Acceso Personal de GitHub (con permisos de lectura para repos y PRs).
    GITHUB_PAT="github_pat_..."

    # =================================================
    # === CONFIGURACIÓN PARA AMBOS (API Y AGENTE) ===
    # =================================================

    # La URL de tu nodo de Sepolia (de Infura, Alchemy, etc.).
    SEPOLIA_RPC_URL="https://sepolia.infura.io/v3/TU_API_KEY"

    # La dirección de tu contrato CampaignFactory desplegado.
    FACTORY_ADDRESS="0x...LA_DIRECCION_DE_TU_CONTRATO"

🏃‍♂️ Cómo Correr los Servicios del Backend

Debes ejecutar la API y el Agente en dos terminales separadas.
✅ Terminal 1: Levantar la API

    En una terminal, navega a app-backend y activa el entorno virtual (source venv/bin/activate).

    Establece las variables de entorno para la sesión actual: La API no lee el archivo .env, por lo que debes exportarlas.

    export SEPOLIA_RPC_URL="LA_URL_DE_TU_NODO_SEPOLIA"
    export FACTORY_ADDRESS="LA_DIRECCION_DE_TU_CONTRATO"

    Inicia el servidor:

    uvicorn main:app --reload

    La API estará disponible en http://127.0.0.1:8000.

✅ Terminal 2: Ejecutar el Agente Autónomo

    Abre una nueva terminal, navega a app-backend y activa el entorno virtual.

    El agente leerá las variables del archivo .env, por lo que no necesitas exportarlas.

    Inicia el agente:

    python agent.py

    Verás en la consola cómo el agente empieza a escanear la blockchain en busca de trabajo.

📈 Estado del Proyecto

✅ Backend FastAPI y Agente 100% Operativos. ✅ Integración Completa con la Blockchain: Lee datos de los contratos y envía transacciones de forma autónoma.

✅ Verificación de GitHub Funcional: El agente puede confirmar la fusión de Pull Requests.

🔜 Próximos Pasos: Migrar el almacenamiento de metadatos a una base de datos real (ej. PostgreSQL) para mejorar la eficiencia y añadir capacidades de búsqueda y filtrado.
