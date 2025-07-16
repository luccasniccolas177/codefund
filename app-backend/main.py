# -----------------------------------------------------------------------------
# DApp Backend (Versión Corregida y Robusta)
# -----------------------------------------------------------------------------
import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3
from datetime import datetime

# --- Configuración Inicial ---
app = FastAPI(
    title="CodeFund API",
    description="API para la DApp de Crowdfunding CodeFund, con lógica de Dashboard.",
    version="1.3.1"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Conexión a la Blockchain ---
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
FACTORY_ADDRESS = os.getenv("FACTORY_ADDRESS")
if not SEPOLIA_RPC_URL or not FACTORY_ADDRESS:
    raise RuntimeError("Error: Las variables de entorno SEPOLIA_RPC_URL y FACTORY_ADDRESS deben estar definidas.")
w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))

# --- ABIs de los Contratos ---
FACTORY_ABI = json.loads('[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"campaignAddress","type":"address"},{"indexed":true,"internalType":"address","name":"developer","type":"address"},{"indexed":false,"internalType":"string","name":"name","type":"string"}],"name":"CampaignCreated","type":"event"},{"inputs":[{"internalType":"string","name":"_name","type":"string"},{"internalType":"string","name":"_description","type":"string"},{"internalType":"string","name":"_githubUrl","type":"string"},{"internalType":"uint256","name":"_fundingGoal","type":"uint256"},{"internalType":"uint256","name":"_deadline","type":"uint256"},{"internalType":"string[]","name":"_milestoneDescriptions","type":"string[]"},{"internalType":"uint256[]","name":"_milestoneAmounts","type":"uint256[]"},{"internalType":"string[]","name":"_milestoneUrls","type":"string[]"}],"name":"createCampaign","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getDeployedCampaigns","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"}]')
CAMPAIGN_ABI = json.loads('[{"inputs":[{"internalType":"string","name":"_name","type":"string"},{"internalType":"string","name":"_description","type":"string"},{"internalType":"string","name":"_githubUrl","type":"string"},{"internalType":"uint256","name":"_fundingGoal","type":"uint256"},{"internalType":"uint256","name":"_deadline","type":"uint256"},{"internalType":"address","name":"_developer","type":"address"},{"internalType":"string[]","name":"_milestoneDescriptions","type":"string[]"},{"internalType":"uint256[]","name":"_milestoneAmounts","type":"uint256[]"},{"internalType":"string[]","name":"_milestoneUrls","type":"string[]"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"contributor","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Contribution","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"milestoneId","type":"uint256"},{"indexed":false,"internalType":"string","name":"description","type":"string"}],"name":"MilestoneCreated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"milestoneId","type":"uint256"},{"indexed":true,"internalType":"address","name":"approver","type":"address"}],"name":"MilestoneApproved","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"milestoneId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"FundsReleased","type":"event"},{"inputs":[{"internalType":"uint256","name":"_milestoneId","type":"uint256"}],"name":"approveMilestone","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"contribute","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"contributions","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"contributorCount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"_description","type":"string"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"createMilestone","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"deadline","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"developer","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"fundingGoal","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getCampaignDetails","outputs":[{"internalType":"string","name":"","type":"string"},{"internalType":"string","name":"","type":"string"},{"internalType":"string","name":"","type":"string"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getMilestones","outputs":[{"components":[{"internalType":"string","name":"description","type":"string"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"string","name":"verificationUrl","type":"string"},{"internalType":"bool","name":"verified","type":"bool"},{"internalType":"bool","name":"fundsReleased","type":"bool"}],"internalType":"struct Campaign.Milestone[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_milestoneId","type":"uint256"}],"name":"releaseMilestoneFunds","outputs":[],"stateMutability":"nonpayable","type":"function"}]')

# --- Modelos de Datos (Pydantic) ---
class Milestone(BaseModel):
    description: str; amount_eth: float; verified: bool; funds_released: bool; verificationUrl: str
class ProjectDetail(BaseModel):
    campaign_address: str; developer_address: str; name: str; description: str; githubUrl: str; funding_goal_eth: float; total_raised_eth: float; contributor_count: int; deadline_formatted: str; days_left: int; milestones: List[Milestone]
class ProjectSummary(BaseModel):
    campaign_address: str; name: str; description: str; funding_goal_eth: float; total_raised_eth: float; developer_address: str; deadline_formatted: str; days_left: int

# --- Función Auxiliar para procesar fechas de forma segura ---
def safe_process_date(timestamp):
    try:
        date_obj = datetime.fromtimestamp(timestamp)
        days_left = (date_obj - datetime.now()).days
        return date_obj.strftime("%d/%m/%Y"), max(0, days_left)
    except (OSError, ValueError):
        # Si el timestamp es inválido (ej. muy lejano), devuelve valores seguros
        print(f"Advertencia: Timestamp inválido encontrado: {timestamp}")
        return "Fecha inválida", 0

# --- Función Auxiliar para obtener todos los proyectos ---
def get_all_campaign_details():
    factory_contract = w3.eth.contract(address=FACTORY_ADDRESS, abi=FACTORY_ABI)
    campaign_addresses = factory_contract.functions.getDeployedCampaigns().call()
    all_projects = []
    for address in campaign_addresses:
        campaign_contract = w3.eth.contract(address=address, abi=CAMPAIGN_ABI)
        details = campaign_contract.functions.getCampaignDetails().call()
        contributions_func = campaign_contract.functions.contributions
        all_projects.append({"address": address, "details": details, "contributions_func": contributions_func})
    return all_projects

# --- Endpoints de la API ---
@app.get("/")
def read_root(): return {"message": "Bienvenido a la API de CodeFund"}

@app.get("/api/v1/projects", response_model=List[ProjectSummary])
async def get_all_projects():
    projects_list = []
    try:
        all_campaigns = get_all_campaign_details()
        for campaign in all_campaigns:
            details = campaign["details"]
            deadline_formatted, days_left = safe_process_date(details[4])
            projects_list.append(ProjectSummary(
                name=details[0], description=details[1], funding_goal_eth=float(w3.from_wei(details[3], 'ether')),
                deadline_formatted=deadline_formatted, days_left=days_left,
                total_raised_eth=float(w3.from_wei(details[5], 'ether')), developer_address=details[6], campaign_address=campaign["address"]
            ))
        return projects_list[::-1]
    except Exception as e:
        print(f"Error al contactar la blockchain: {e}")
        raise HTTPException(status_code=500, detail="No se pudo obtener la información de la blockchain.")

@app.get("/api/v1/projects/{campaign_address}", response_model=ProjectDetail)
async def get_project_by_address(campaign_address: str):
    try:
        campaign_contract = w3.eth.contract(address=campaign_address, abi=CAMPAIGN_ABI)
        details_tuple = campaign_contract.functions.getCampaignDetails().call()
        milestones_tuple = campaign_contract.functions.getMilestones().call()
        
        deadline_formatted, days_left = safe_process_date(details_tuple[4])
        contributor_count = campaign_contract.functions.contributorCount().call()

        milestones_list = [Milestone(description=m[0], amount_eth=float(w3.from_wei(m[1], 'ether')), verificationUrl=m[2], verified=m[3], funds_released=m[4]) for m in milestones_tuple]
        
        return ProjectDetail(
            name=details_tuple[0], description=details_tuple[1], githubUrl=details_tuple[2],
            funding_goal_eth=float(w3.from_wei(details_tuple[3], 'ether')),
            total_raised_eth=float(w3.from_wei(details_tuple[5], 'ether')), 
            contributor_count=contributor_count,
            developer_address=details_tuple[6], 
            deadline_formatted=deadline_formatted,
            days_left=days_left, 
            campaign_address=campaign_address, 
            milestones=milestones_list
        )
    except Exception as e:
        print(f"Error al obtener detalles del proyecto {campaign_address}: {e}")
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o error en la blockchain.")

# --- Endpoints para el Dashboard ---
@app.get("/api/v1/users/{user_address}/created", response_model=List[ProjectSummary])
async def get_created_campaigns(user_address: str):
    user_campaigns = []
    normalized_user_address = user_address.lower()
    try:
        all_campaigns = get_all_campaign_details()
        for campaign in all_campaigns:
            details = campaign["details"]
            if details[6].lower() == normalized_user_address:
                deadline_formatted, days_left = safe_process_date(details[4])
                user_campaigns.append(ProjectSummary(
                    name=details[0], description=details[1], funding_goal_eth=float(w3.from_wei(details[3], 'ether')),
                    deadline_formatted=deadline_formatted, days_left=days_left,
                    total_raised_eth=float(w3.from_wei(details[5], 'ether')), developer_address=details[6], campaign_address=campaign["address"]
                ))
        return user_campaigns[::-1]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las campañas creadas: {e}")

@app.get("/api/v1/users/{user_address}/contributed", response_model=List[ProjectSummary])
async def get_contributed_campaigns(user_address: str):
    user_contributions = []
    try:
        all_campaigns = get_all_campaign_details()
        for campaign in all_campaigns:
            contribution_amount = campaign["contributions_func"](user_address).call()
            if contribution_amount > 0:
                details = campaign["details"]
                deadline_formatted, days_left = safe_process_date(details[4])
                user_contributions.append(ProjectSummary(
                    name=details[0], description=details[1], funding_goal_eth=float(w3.from_wei(details[3], 'ether')),
                    deadline_formatted=deadline_formatted, days_left=days_left,
                    total_raised_eth=float(w3.from_wei(details[5], 'ether')), developer_address=details[6], campaign_address=campaign["address"]
                ))
        return user_contributions[::-1]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las contribuciones: {e}")
