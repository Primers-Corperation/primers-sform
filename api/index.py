from fastapi import FastAPI
import os
import sys

app = FastAPI(title="Primers Diagnostic")

@app.get("/api")
def root():
    return {
        "system": "PRIMERS GPT",
        "status": "ONLINE",
        "version": "2.0.0",
        "vercel": True,
        "python": sys.version,
        "cwd": os.getcwd(),
        "files": os.listdir(".")
    }

@app.get("/api/compliance")
def compliance():
    return {
        "score": 100,
        "status": "SOVEREIGN_COMPLIANT",
        "audit_trail": "ACTIVE"
    }
