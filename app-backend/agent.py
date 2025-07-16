import os
import re
import time
import json
import requests
from dotenv import load_dotenv
from web3 import Web3

# --- Configuración y Carga de Secretos ---
load_dotenv()

RPC_URL = os.getenv("SEPOLIA_RPC_URL")
FACTORY_ADDRESS = os.getenv("FACTORY_ADDRESS")
AGENT_PRIVATE_KEY = os.getenv("AGENT_PRIVATE_KEY")
GITHUB_PAT = os.getenv("GITHUB_PAT")

if not all([RPC_URL, FACTORY_ADDRESS, AGENT_PRIVATE_KEY, GITHUB_PAT]):
    raise ValueError("Una o más variables de entorno críticas no están definidas.")

# --- Conexión a la Blockchain y Configuración de la Cuenta del Agente ---
w3 = Web3(Web3.HTTPProvider(RPC_URL))
agent_account = w3.eth.account.from_key(AGENT_PRIVATE_KEY)
print(f"🤖 Agente iniciado. Dirección del agente: {agent_account.address}")

# --- ABIs (deben coincidir con los contratos desplegados) ---
FACTORY_ABI = json.loads('[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"campaignAddress","type":"address"},{"indexed":true,"internalType":"address","name":"developer","type":"address"},{"indexed":false,"internalType":"string","name":"name","type":"string"}],"name":"CampaignCreated","type":"event"},{"inputs":[{"internalType":"string","name":"_name","type":"string"},{"internalType":"string","name":"_description","type":"string"},{"internalType":"string","name":"_githubUrl","type":"string"},{"internalType":"uint256","name":"_fundingGoal","type":"uint256"},{"internalType":"uint256","name":"_deadline","type":"uint256"},{"internalType":"string[]","name":"_milestoneDescriptions","type":"string[]"},{"internalType":"uint256[]","name":"_milestoneAmounts","type":"uint256[]"},{"internalType":"string[]","name":"_milestoneUrls","type":"string[]"}],"name":"createCampaign","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getDeployedCampaigns","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"}]')
CAMPAIGN_ABI = json.loads('[{"inputs":[{"internalType":"string","name":"_name","type":"string"},{"internalType":"string","name":"_description","type":"string"},{"internalType":"string","name":"_githubUrl","type":"string"},{"internalType":"uint256","name":"_fundingGoal","type":"uint256"},{"internalType":"uint256","name":"_deadline","type":"uint256"},{"internalType":"address","name":"_developer","type":"address"},{"internalType":"string[]","name":"_milestoneDescriptions","type":"string[]"},{"internalType":"uint256[]","name":"_milestoneAmounts","type":"uint256[]"},{"internalType":"string[]","name":"_milestoneUrls","type":"string[]"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"contributor","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Contribution","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"milestoneId","type":"uint256"},{"indexed":false,"internalType":"string","name":"description","type":"string"}],"name":"MilestoneCreated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"milestoneId","type":"uint256"},{"indexed":true,"internalType":"address","name":"approver","type":"address"}],"name":"MilestoneApproved","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"milestoneId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"FundsReleased","type":"event"},{"inputs":[{"internalType":"uint256","name":"_milestoneId","type":"uint256"}],"name":"approveMilestone","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"contribute","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"getCampaignDetails","outputs":[{"internalType":"string","name":"","type":"string"},{"internalType":"string","name":"","type":"string"},{"internalType":"string","name":"","type":"string"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getMilestones","outputs":[{"components":[{"internalType":"string","name":"description","type":"string"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"string","name":"verificationUrl","type":"string"},{"internalType":"bool","name":"verified","type":"bool"},{"internalType":"bool","name":"fundsReleased","type":"bool"}],"internalType":"struct Campaign.Milestone[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_milestoneId","type":"uint256"}],"name":"releaseMilestoneFunds","outputs":[],"stateMutability":"nonpayable","type":"function"}]')

# --- Lógica de Verificación ---
def check_github_pr_merged(pr_url: str) -> bool:
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        print(f"  - URL de PR no válida: {pr_url}")
        return False
    owner, repo, pr_number = match.groups()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {"Authorization": f"token {GITHUB_PAT}"}
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        is_merged = response.json().get("merged", False)
        print(f"  - Verificando PR #{pr_number}: {'Fusionado' if is_merged else 'No fusionado'}")
        return is_merged
    except requests.exceptions.RequestException as e:
        print(f"  - Error al consultar la API de GitHub: {e}")
        return False

# --- Lógica On-Chain (Función Corregida) ---
def approve_milestone_onchain(campaign_address: str, milestone_index: int):
    """Envía una transacción para aprobar un hito en la blockchain."""
    try:
        campaign_contract = w3.eth.contract(address=campaign_address, abi=CAMPAIGN_ABI)
        nonce = w3.eth.get_transaction_count(agent_account.address)

        # Construir la transacción
        tx = campaign_contract.functions.approveMilestone(milestone_index).build_transaction({
            'from': agent_account.address,
            'nonce': nonce,
            'gas': 200000, # Límite de gas razonable
            'gasPrice': w3.eth.gas_price
        })

        # Firmar la transacción
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=AGENT_PRIVATE_KEY)
        
        # --- CORRECCIÓN FINAL ---
        # El atributo correcto es .raw_transaction (con guion bajo)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"  ✅ Transacción de aprobación enviada. Hash: {tx_hash.hex()}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"  🎉 ¡Hito {milestone_index} aprobado en el bloque {receipt.blockNumber}!")

    except Exception as e:
        print(f"  ❌ Error al enviar la transacción de aprobación: {e}")
        # En caso de que el error persista, imprimimos los atributos del objeto para depurar
        if 'signed_tx' in locals():
            print("  - Atributos del objeto 'signed_tx':", dir(signed_tx))

# --- Orquestador Principal del Agente ---
def run_agent_cycle():
    print("\n--- 🔄 Iniciando nuevo ciclo de verificación ---")
    factory_contract = w3.eth.contract(address=FACTORY_ADDRESS, abi=FACTORY_ABI)
    try:
        campaign_addresses = factory_contract.functions.getDeployedCampaigns().call()
        print(f"🔎 Encontradas {len(campaign_addresses)} campañas para revisar.")
        for address in campaign_addresses:
            print(f"\n🔍 Revisando campaña: {address}")
            campaign_contract = w3.eth.contract(address=address, abi=CAMPAIGN_ABI)
            milestones = campaign_contract.functions.getMilestones().call()
            for i, milestone in enumerate(milestones):
                is_verified = milestone[3]
                is_released = milestone[4]
                verification_url = milestone[2]
                if not is_verified and not is_released and verification_url.startswith("https://github.com"):
                    print(f"  - Hito pendiente encontrado (#{i}): {milestone[0]}")
                    if check_github_pr_merged(verification_url):
                        print(f"  - Condición cumplida. Procediendo a aprobar en la blockchain...")
                        approve_milestone_onchain(address, i)
                    else:
                        print(f"  - Condición aún no cumplida.")
    except Exception as e:
        print(f"🚨 Error mayor durante el ciclo del agente: {e}")

if __name__ == "__main__":
    while True:
        try:
            run_agent_cycle()
            sleep_duration = 60
            print(f"\n--- ✅ Ciclo completado. Durmiendo por {sleep_duration} segundos. ---")
            time.sleep(sleep_duration)
        except KeyboardInterrupt:
            print("\n🛑 Agente detenido manualmente. ¡Adiós!")
            break
