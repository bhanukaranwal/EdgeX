"""
server.py
Interactive FastAPI server for UI control and monitoring.
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, WebSocket
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List
from edgeX.utils.logger import get_logger

app = FastAPI(title="EdgeX Trading Bot UI")
logger = get_logger("EdgeXUI")
security = HTTPBasic()

USERS = {"admin": "supersecret"}  # Extend with secure auth in production.

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if USERS.get(credentials.username) == credentials.password:
        return True
    raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/status")
def get_status(auth: bool = Depends(authenticate)):
    logger.info("[UI] Status queried.")
    return {"status": "running", "version": "0.1.0"}

@app.post("/start")
def start_bot(auth: bool = Depends(authenticate)):
    logger.info("[UI] Bot start requested.")
    return {"message": "Bot start triggered."}

@app.post("/stop")
def stop_bot(auth: bool = Depends(authenticate)):
    logger.info("[UI] Bot stop requested.")
    return {"message": "Bot stop triggered."}

@app.post("/update_params")
def update_params(params: dict, auth: bool = Depends(authenticate)):
    logger.info(f"[UI] Params update requested: {params}")
    return {"message": "Parameters updated.", "params": params}

@app.get("/orders", response_model=List[dict])
def get_latest_orders(auth: bool = Depends(authenticate)):
    logger.info("[UI] Orders requested.")
    return []

@app.get("/logs", response_model=List[str])
def get_logs(lines: int = 100, auth: bool = Depends(authenticate)):
    try:
        with open("logs/edgex.log") as f:
            log_data = f.readlines()[-lines:]
        return log_data
    except Exception as e:
        logger.error(f"[UI] Log fetch error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_config/")
def upload_config(file: UploadFile = File(...), auth: bool = Depends(authenticate)):
    try:
        fname = f"config/{file.filename}"
        with open(fname, "wb") as buffer:
            buffer.write(file.file.read())
        logger.info(f"[UI] Config uploaded: {fname}")
        return {"message": f"Config {file.filename} uploaded!"}
    except Exception as e:
        logger.error(f"[UI] Config upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/live_quotes")
async def ws_live_quotes(websocket: WebSocket):
    await websocket.accept()
    import asyncio
    while True:
        # Placeholder for live quote pushing, e.g. fetch from market data module
        ltp = {"symbol": "NIFTY", "price": 23450.10, "timestamp": "2025-08-09T11:25:34"}
        await websocket.send_json(ltp)
        await asyncio.sleep(1)
