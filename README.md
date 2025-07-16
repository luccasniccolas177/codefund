¡Excelente pregunta\! Es una duda muy importante para la entrega de tu proyecto.

**Respuesta corta:** Tu profesor **no** deberá crear el contrato. Tú debes desplegarlo, obtener la dirección y poner esa misma dirección en los archivos de configuración tanto del frontend como del backend.

**Explicación:** Piensa que tu contrato desplegado es como la base de datos central de tu aplicación. Para que el frontend, el backend y el agente puedan "hablar" entre sí y ver la misma información, todos deben apuntar a la **misma dirección de contrato**. Si tu profesor desplegara uno nuevo, estaría vacío y la aplicación no mostraría nada.

Por eso, en el `README` he incluido una sección clara para que tu profesor sepa que el primer paso es desplegar el contrato y luego usar esa dirección para configurar el resto.

Aquí tienes el `README` del backend, completamente formateado y listo para copiar y pegar, incluyendo esa sección.

-----

````
# CodeFund Backend - API y Agente de Verificación Autónomo

Este repositorio contiene el código fuente del backend para **CodeFund**, compuesto por dos servicios principales escritos en Python:

1.  **Una API RESTful (FastAPI):** Actúa como un puente eficiente entre el frontend y la blockchain. Proporciona endpoints para consultar información de campañas y usuarios de forma rápida, evitando que el frontend tenga que hacer costosas llamadas a la blockchain para cada vista.
2.  **Un Agente de Verificación Autónomo:** Un script independiente que se ejecuta en segundo plano. Su misión es monitorear la blockchain, verificar las condiciones de los hitos en GitHub y enviar transacciones para aprobarlos automáticamente.

---

## 🚀 Funcionalidades Implementadas

### API RESTful (main.py)
- Endpoints para listar todos los proyectos (`/api/v1/projects`).
- Endpoint para ver los detalles completos de un proyecto, incluyendo sus hitos (`/api/v1/projects/{address}`).
- Endpoints para el Dashboard de usuario: listar proyectos creados (`/users/{address}/created`) y contribuidos (`/users/{address}/contributed`).

### Agente de Verificación (agent.py)
- Escanea periódicamente todas las campañas en la blockchain.
- Para los hitos pendientes, extrae la URL de verificación (ej. un Pull Request de GitHub).
- Usa la API de GitHub para comprobar si el PR ha sido fusionado ("merged").
- Si la condición se cumple, utiliza su propia wallet para enviar una transacción on-chain y aprobar el hito en el contrato inteligente correspondiente.

---

## 🛠️ Pila Tecnológica

- **Framework API:** FastAPI
- **Servidor ASGI:** Uvicorn
- **Interacción Blockchain:** Web3.py
- **Cliente HTTP (Agente):** Requests
- **Gestión de Secretos:** python-dotenv
- **Lenguaje:** Python 3.10+

---

## ⚙️ Instalación y Configuración

Para ejecutar este proyecto completo, se deben poner en marcha 3 componentes: el **Contrato Inteligente**, la **API** y el **Agente**.

### Requisitos Previos
- [Python](https://www.python.org/downloads/) (versión 3.10 o superior)
- ETH de prueba en la red Sepolia (puedes obtenerlo de un [faucet](https://sepoliafaucet.com/))

### Parte 1: Desplegar el Contrato Inteligente

Este es el primer paso y el más importante, ya que tanto la API como el Agente dependen de la dirección del contrato.

1.  **Abre Remix IDE:** Ve a [remix.ethereum.org](https://remix.ethereum.org/).
2.  **Crea el archivo:** Crea un nuevo archivo `CodeFund.sol` y pega el contenido del contrato inteligente del proyecto.
3.  **Compila:** Ve a la pestaña "Solidity Compiler", selecciona una versión del compilador `0.8.20` o superior y haz clic en "Compile".
4.  **Despliega:**
    - Ve a la pestaña "Deploy & Run Transactions".
    - En el menú "ENVIRONMENT", selecciona **"Injected Provider - MetaMask"**. Conecta tu wallet y asegúrate de estar en la red **Sepolia**.
    - En el menú desplegable "CONTRACT", selecciona `CampaignFactory`.
    - Haz clic en el botón naranja **"Deploy"** y confirma la transacción en MetaMask.
5.  **Copia la Dirección del Contrato:** Una vez confirmada, copia la dirección del contrato `CampaignFactory` desplegado. La necesitarás para todos los siguientes pasos.

### Parte 2: Configurar y Ejecutar el Backend

1.  **Clona el repositorio y navega a la carpeta:**
    ```bash
    git clone <repo_url>
    cd <nombre_del_repo>/app-backend
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En macOS / Linux
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install fastapi "uvicorn[standard]" web3 python-dotenv requests
    ```

4.  **Configura las variables de entorno:**
    - Crea un archivo llamado `.env` en la raíz de `app-backend`.
    - Pega el siguiente contenido y rellena tus datos. **Usa la dirección del contrato que desplegaste en la Parte 1.**

    ```
    # =================================================
    # === CONFIGURACIÓN PARA EL AGENTE (agent.py) ===
    # =================================================
    AGENT_PRIVATE_KEY="LA_CLAVE_PRIVADA_DE_LA_WALLET_DEL_AGENTE"
    GITHUB_PAT="TU_TOKEN_DE_ACCESO_PERSONAL_DE_GITHUB"

    # =================================================
    # === CONFIGURACIÓN PARA AMBOS (API Y AGENTE) ===
    # =================================================
    SEPOLIA_RPC_URL="LA_URL_DE_TU_NODO_SEPOLIA_DE_INFURA_O_ALCHEMY"
    FACTORY_ADDRESS="LA_DIRECCION_DEL_CONTRATO_QUE_DESPLEGASTE_EN_LA_PARTE_1"
    ```

---

## 🏃‍♂️ Cómo Correr los Servicios del Backend

Debes ejecutar la API y el Agente en **dos terminales separadas**.

### ✅ Terminal 1: Levantar la API

1.  En una terminal, navega a `app-backend` y activa el entorno virtual (`source venv/bin/activate`).
2.  **Establece las variables de entorno para la sesión actual:** La API no lee el archivo `.env`, por lo que debes exportarlas.
    ```bash
    export SEPOLIA_RPC_URL="LA_URL_DE_TU_NODO_SEPOLIA"
    export FACTORY_ADDRESS="LA_DIRECCION_DE_TU_CONTRATO"
    ```
3.  **Inicia el servidor:**
    ```bash
    uvicorn main:app --reload
    ```
    La API estará disponible en `http://127.0.0.1:8000`.

### ✅ Terminal 2: Ejecutar el Agente Autónomo

1.  Abre una **nueva terminal**, navega a `app-backend` y activa el entorno virtual.
2.  El agente leerá las variables del archivo `.env`, por lo que no necesitas exportarlas aquí.
3.  **Inicia el agente:**
    ```bash
    python agent.py
    ```
    Verás en la consola cómo el agente empieza a escanear la blockchain en busca de trabajo.

---

## 📈 Estado del Proyecto

- **Backend FastAPI y Agente 100% Operativos.**
- **Integración Completa con la Blockchain:** Lee datos de los contratos y envía transacciones de forma autónoma.
- **Verificación de GitHub Funcional:** El agente puede confirmar la fusión de Pull Requests.
- **Próximos Pasos:** Migrar el almacenamiento de metadatos a una base de datos real (ej. PostgreSQL) para mejorar la eficiencia y añadir capacidades de búsqueda y filtrado.

````
