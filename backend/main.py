from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from core.engine import PrimersEngine
from core.report_generator import SovereignReportGenerator
from core.auth import authenticate, validate_token, require_permission, revoke_token
from core.compliance import get_compliance_report
from fastapi import Header
import os
import uvicorn
import time
import psutil
import sqlite3
import tempfile
from dotenv import load_dotenv

load_dotenv()
BOOT_TIME = time.time()

app = FastAPI(
    title="PrimersGPT", 
    description="Sovereign Intelligence Backend", 
    version="2.0.0",
    root_path="/api" if os.getenv("VERCEL") else ""
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = PrimersEngine()

# Phase 5: Auto-Ingest current directory on startup
@app.on_event("startup")
async def startup_event():
    if not os.getenv("VERCEL"):
        print("Initial Scan: Ingesting local workspace...")
        engine.process("ingest .")
    else:
        print("Vercel detected: Skipping auto-ingest.")

class ChatRequest(BaseModel):
    message: str
    mode: str = "default"

class IngestRequest(BaseModel):
    target: str # e.g. "github"
    params: dict 

@app.get("/")
def read_root():
    return {"system": "PRIMERS GPT", "status": "ONLINE", "version": "2.5.0"}

@app.get("/compliance")
async def compliance_status():
    return get_compliance_report()

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    response_obj = engine.process(request.message, mode=request.mode)
    # Convert dataclass to dict for JSON serialization
    return {"response": response_obj.to_dict()}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    try:
        content_str = content.decode("utf-8")
    except:
        content_str = "[Binary Data]"

    # Route to engine as a special "upload" command
    msg = f"upload file: {file.filename}\ncontent: {content_str}"
    response_obj = engine.process(msg)
    return {"response": response_obj.to_dict()}

@app.post("/emergency/witness")
async def emergency_witness(file: UploadFile = File(...)):
    image_data = await file.read()
    res = engine.emergency.analyze_witness_image(image_data)
    return res

@app.post("/emergency/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    if engine.emergency.status["whisper_voice"] == "READY":
        # TODO: Move model loading to Intelligence engine initialization when weights are mounted.
        # Current cold-load per request is for demo flexibility but will timeout on serverless.
        import whisper
        # Load model using the configured path
        model = whisper.load_model("base", download_root=engine.emergency.models_config["whisper_voice"])
        
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False, dir="/tmp") as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name
        
        try:
            result = model.transcribe(tmp_path)
            return {"transcript": result["text"]}
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    else:
        # Sovereign simulation fallback
        return {
            "transcript": engine.emergency.transcribe_voice_guardian(None),
            "mode": "SIMULATED"
        }

@app.post("/auth/login")
async def login(payload: dict):
    username = payload.get("username", "")
    password = payload.get("password", "")
    session = authenticate(username, password)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return session

@app.post("/auth/logout")
async def logout(payload: dict):
    revoke_token(payload.get("token", ""))
    return {"status": "SESSION_TERMINATED"}

@app.get("/auth/validate")
async def validate_session(authorization: str = Header(None)):
    token = authorization.replace("Bearer ", "") if authorization else ""
    session = validate_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    return session

@app.post("/emergency/report")
async def generate_report(payload: dict, authorization: str = Header(None)):
    token = authorization.replace("Bearer ", "") if authorization else ""
    if not require_permission(token, "export_report"):
        raise HTTPException(status_code=403, detail="INSUFFICIENT_CLEARANCE")
    generator = SovereignReportGenerator()
    filepath = generator.generate_incident_report(
        audit_log=payload.get("audit_log", []),
        triage_results=payload.get("triage_results", []),
        detr_results=payload.get("detr_results", []),
        operator=payload.get("operator", "GOV-DEF-01"),
        incident_id=payload.get("incident_id", None)
    )
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=os.path.basename(filepath)
    )

@app.post("/ingest")
async def ingest_endpoint(request: IngestRequest):
    if request.target == "github":
        username = request.params.get("username")
        if not username:
             raise HTTPException(400, "Username required")
        
        # Route through the core engine process
        response_obj = engine.process(f"learn from github {username}")
        return {"status": "success", "response": response_obj.to_dict()}
    
    return {"status": "error", "message": "Unknown target"}

@app.get("/stats")
async def get_stats():
    # Knowledge stats
    db_path = engine.m2.db_path
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM repo_analysis")
            knowledge_nodes = cursor.fetchone()[0]
    except:
        knowledge_nodes = 0
    
    # System Stats
    try:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
    except:
        cpu, mem = 0, 0
    
    # Uptime calc
    uptime_sec = int(time.time() - BOOT_TIME)
    h = uptime_sec // 3600
    m = (uptime_sec % 3600) // 60
    uptime_str = f"{h}h {m}m"

    # Health score
    from core.types import TraceLog
    from core.reasoning import ReasoningGraph
    try:
        graph = ReasoningGraph(TraceLog(session_id="stats_check"))
        health_res = engine._handle_health_check(graph)
        health_score = health_res.meta.get("health_score", 100)
    except Exception as e:
        print(f"Health check failed: {e}")
        health_score = 100

    # Proactive Auditor logic
    proactive_alert = engine.auditor.prepare_proactive_alert(health_score)

    # Emergency status (Phase 5 Extension)
    emergency_status = engine.emergency.get_emergency_status()

    return {
        "cpu": cpu,
        "memory": mem,
        "knowledge_nodes": knowledge_nodes,
        "uptime": uptime_str,
        "intelligence_mode": "SOVEREIGN_CLOUD_HYBRID" if engine.model else "HYBRID_HEURISTIC",
        "health_score": health_score,
        "proactive_alert": proactive_alert,
        "emergency_status": emergency_status
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
