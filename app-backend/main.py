from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

# --- Modelos de Datos (Pydantic) ---
# Definen la estructura de los datos que se envían y reciben en la API.

class Milestone(BaseModel):
    id: int
    description: str
    funds_to_release: float
    deadline: str # Usamos string para simplicidad en el mock
    verified: bool = False
    funds_released: bool = False

class Project(BaseModel):
    campaign_address: str = Field(..., example="0x1234567890123456789012345678901234567890")
    developer_address: str = Field(..., example="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd")
    name: str = Field(..., example="Mi Proyecto Increíble")
    description: str = Field(..., example="Una descripción detallada de mi proyecto.")
    funding_goal_eth: float = Field(..., example=10.0)
    total_raised_eth: float = Field(..., example=1.5)
    deadline: str # Usamos string para simplicidad en el mock
    github_url: str = Field(..., example="https://github.com/user/repo")
    milestones: List[Milestone] = []

# --- Base de Datos Mock ---
# En una aplicación real, estos datos vendrían de una base de datos como PostgreSQL
# y se sincronizarían con los eventos de la blockchain.
MOCK_DB: List[Project] = [
    Project(
        campaign_address="0x1234567890123456789012345678901234567890",
        developer_address="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
        name="Agente de Verificación IA",
        description="Un bot que usa LLMs para analizar la calidad de los commits en repositorios de GitHub.",
        funding_goal_eth=10.0,
        total_raised_eth=8.5,
        deadline="2025-08-15T23:59:59Z",
        github_url="https://github.com/codex-ia/verifier-agent",
        milestones=[
            Milestone(id=1, description="Conectar a la API de GitHub y extraer commits.", funds_to_release=2.0, deadline="2025-07-20T23:59:59Z", verified=True, funds_released=True),
            Milestone(id=2, description="Implementar análisis heurístico (conteo de PRs).", funds_to_release=3.0, deadline="2025-07-30T23:59:59Z", verified=True, funds_released=False),
            Milestone(id=3, description="Integrar con API de LLM para análisis semántico.", funds_to_release=5.0, deadline="2025-08-15T23:59:59Z", verified=False, funds_released=False),
        ]
    ),
    Project(
        campaign_address="0xabcdef123456789012345678901234567890abcd",
        developer_address="0x1234567890abcdef1234567890abcdef12345678",
        name="Librería de Gráficos Web3",
        description="Una librería de componentes React para visualizar datos on-chain de forma sencilla.",
        funding_goal_eth=5.0,
        total_raised_eth=1.2,
        deadline="2025-09-01T23:59:59Z",
        github_url="https://github.com/web3-charts/react-web3-viz",
        milestones=[]
    )
]

# --- Inicialización de la App FastAPI ---
app = FastAPI(
    title="CodeFund API",
    description="API para la DApp de Crowdfunding CodeFund.",
    version="1.0.0"
)

# Configuración de CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # La URL donde corre el frontend de Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Endpoints de la API ---

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de CodeFund"}

@app.get("/api/v1/projects", response_model=List[Project])
async def get_all_projects():
    """
    Devuelve una lista de todos los proyectos de crowdfunding.
    En el futuro, esto consultará la base de datos que se sincroniza con la blockchain.
    """
    return MOCK_DB

@app.get("/api/v1/projects/{campaign_address}", response_model=Project)
async def get_project_by_address(campaign_address: str):
    """
    Devuelve los detalles de un proyecto específico por su dirección de contrato.
    """
    # Lógica para buscar el proyecto en la base de datos mock
    project = next((p for p in MOCK_DB if p.campaign_address == campaign_address), None)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # --- LÓGICA WEB3 (FUTURA) ---
    # Aquí es donde se enriquecerían los datos con información fresca de la blockchain.
    # try:
    #     from web3 import Web3
    #     # Conectar a un nodo de Arbitrum (ej. usando Infura o Alchemy)
    #     w3 = Web3(Web3.HTTPProvider('https://arbitrum-mainnet.infura.io/v3/TU_PROJECT_ID'))
    #     # Cargar el ABI del contrato Campaign
    #     campaign_contract = w3.eth.contract(address=campaign_address, abi=CAMPAIGN_ABI)
    #     # Llamar a una función `view` para obtener el total recaudado
    #     on_chain_raised = campaign_contract.functions.totalRaised().call()
    #     # Actualizar el objeto del proyecto
    #     project.total_raised_eth = w3.from_wei(on_chain_raised, 'ether')
    # except Exception as e:
    #     print(f"No se pudo obtener datos on-chain para {campaign_address}: {e}")
    #     # Se podría devolver el dato cacheado con una advertencia
    
    return project

@app.post("/api/v1/projects", response_model=Project, status_code=201)
async def create_project(project_data: Project):
    """
    Crea un nuevo proyecto.
    En el futuro, esta función:
    1. Validará los datos de entrada.
    2. Guardará los metadatos en la base de datos.
    3. Llamará al contrato `CampaignFactory` en la blockchain para desplegar un nuevo contrato `Campaign`.
    4. Guardará la nueva dirección del contrato y la devolverá.
    """
    print("Datos del nuevo proyecto recibido:", project_data.dict())
    
    # --- LÓGICA WEB3 (FUTURA) ---
    # Aquí se llamaría al contrato factory para crear la campaña en la blockchain.
    # La dirección `campaign_address` sería generada por esa transacción.
    
    # Simulación: se añade a la base de datos mock
    new_project = project_data.copy(deep=True)
    new_project.campaign_address = f"0x{len(MOCK_DB) + 1:040x}" # Generar una dirección falsa
    MOCK_DB.append(new_project)
    
    return new_project

