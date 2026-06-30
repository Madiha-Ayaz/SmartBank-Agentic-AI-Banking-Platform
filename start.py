import sys
import traceback

try:
    from backend.main import app
    import uvicorn
    port = int(__import__('os').environ.get("PYTHON_PORT", 8000))
    print(f"Starting Python backend on port {port}")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)
except Exception:
    traceback.print_exc()
    sys.exit(1)
