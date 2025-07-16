# CodeFund Backend - API REST con FastAPI

Este proyecto es el backend de **CodeFund**, una plataforma de crowdfunding basada en Web3 que permite financiar proyectos de forma segura y transparente. La API proporciona datos sobre campañas, milestones y permite crear nuevas campañas. En el futuro, se integrará con smart contracts para sincronizar datos on-chain.

---

## 🚀 Funcionalidad

✅ Proveer endpoints REST para:
- Listar proyectos.
- Ver detalles de un proyecto.
- Crear nuevos proyectos.

✅ Habilitar CORS para comunicación con frontend.  
✅ Base de datos mock (en memoria).  
✅ (Próximamente) Integración con blockchain para datos on-chain.

---

## 🛠️ Tecnologías utilizadas

- **Framework:** FastAPI
- **Servidor ASGI:** Uvicorn
- **Modelado de datos:** Pydantic
- **Lenguaje:** Python 3.10+
- **Web3 (futuro):** Web3.py

---

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone <repo_url>
cd codefund-main
```

---

### 2. Crear entorno virtual (opcional pero recomendado)

```bash
python -m venv venv
source venv/bin/activate          # macOS / Linux
venv\Scripts\activate             # Windows
```

---

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 🏃‍♂️ Cómo correr el backend

Ejecuta el servidor:

```bash
uvicorn main:app --reload --port 8000
```

Ejecuta el agente:

```bash
python3 agent.py
```


La API estará disponible en:

- http://127.0.0.1:8000


---

## 💡 Funcionamiento general

- La API provee endpoints REST para gestionar campañas de crowdfunding.
- Los datos están en memoria como listas mock.
- Está preparado para integrarse en el futuro con smart contracts en Solidity para:
  - Validar montos on-chain.
  - Registrar milestones cumplidos.
  - Procesar refunds automáticamente.

---

## 📈 Estado del proyecto

✅ Backend FastAPI operativo.  
✅ Endpoints básicos implementados.  
🔜 Integración real con blockchain (web3.py).  
🔜 Persistencia en base de datos real.


