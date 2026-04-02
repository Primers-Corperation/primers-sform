import os
import sys
import traceback

# Add the backend directory to the path so modules like 'core', 'cognition' etc are found
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, backend_path)

try:
    from main import app as fastapi_app
    app = fastapi_app
except Exception as e:
    # If import fails, create a diagnostic app that reports the error
    from fastapi import FastAPI
    app = FastAPI()
    error_detail = traceback.format_exc()

    @app.get("/")
    def diagnostic_root():
        return {
            "status": "IMPORT_FAILED",
            "error": str(e),
            "traceback": error_detail,
            "python_version": sys.version,
            "cwd": os.getcwd(),
            "root_contents": os.listdir(".") if os.path.exists(".") else [],
            "api_contents": os.listdir("api") if os.path.exists("api") else [],
            "backend_path": backend_path,
            "backend_exists": os.path.exists(backend_path),
            "backend_contents": os.listdir(backend_path) if os.path.exists(backend_path) else []
        }

    @app.get("/{path:path}")
    def diagnostic_catchall(path: str):
        return {
            "status": "IMPORT_FAILED",
            "error": str(e),
            "traceback": error_detail
        }
